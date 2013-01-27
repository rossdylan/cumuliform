from tornado.httpclient import AsyncHTTPClient
from tornado import ioloop
import bs4
import json
import time
import urllib2
import soundcloud
from subprocess import check_call
import shlex


class CumuliformGatherer(object):
    def __init__(self, queue):
        self.client = AsyncHTTPClient()
        self.baseurl = "http://hypem.com/inc/serve_spy.php?page=http%3A//hypem.com/spy&latest={}&ts={}"
        self.queue = queue

    def createUpdateURL(self):
        """
        Create a hypemachine spy update url
        """
        maTime = time.time()
        latest = str(maTime).split(".")[0] + "." + str(maTime).split(".")[1][0:2]
        ts = maTime + 1
        ts = str(ts).split('.')[0]
        return self.baseurl.format(latest, ts)

    def getSoundCloudTrack(self, tag):
        """
        Given a tag containing a soundcloud link find the track index
        :type tag: Tag
        :param tag: A BS4 tag to look through
        """
        for key in tag.attrs:
            val = tag.attrs[key]
            if val == None:
                continue
            try:
                val = urllib2.unquote(val)
            except:
                continue
            if "api.soundcloud.com/tracks" in val:
                val_list = val.split("/")
                track_index = val_list.index("tracks")
                track_id = val_list[track_index + 1]
                if "&" in track_id:
                    track_id = track_id.split("&")[0]
                return track_id
        if tag.string != None:
            if "api.soundcloud.com/tracks" in tag.string:
                str_list = tag.string.split("/")
                track_index = str_list.index("tracks")
                track_id = str_list[track_index + 1]
                if "&" in track_id:
                    track_id = track_id.split("&")[0]
                return track_id
        return ""

    def handleSongURL(self, response):
        if not response.error:
            soup = bs4.BeautifulSoup(response.body)

            def find_sound_cloud(tag):
                for key in tag.attrs:
                    val = tag.attrs[key]
                    if val == None:
                        continue
                    if "api.soundcloud.com" in val:
                        return True

                if tag.string != None and "api.soundcloud.com" in tag.string:
                    return True

                return False
            possible_sc = soup.find_all(find_sound_cloud)
            sc_tracks = map(self.getSoundCloudTrack, possible_sc)
            for track in sc_tracks:
                self.queue.put(track)

    def handleSpyUpdate(self, response):
        if not response.error:
            if response.body != "":
                soup = bs4.BeautifulSoup(response.body)
                script = soup.find_all("script")[-1]
                song_info = json.loads(script.string)
                self.client.fetch(
                    song_info['posturl'],
                    self.handleSongURL,
                    headers={"Referer": "http://hyem.com/spy"})
        self.client.fetch(
            self.createUpdateURL(),
            self.handleSpyUpdate,
            headers={"Referer": "http://hypem.com/spy"},)
        time.sleep(1.5)

    def run(self):
        self.client.fetch(self.createUpdateURL(), self.handleSpyUpdate)
        ioloop.IOLoop.instance().start()


class CumuliformPlayer(object):
    def __init__(self, queue, client_id):
        self.queue = queue
        self.sc_client = soundcloud.Client(client_id=client_id)

    def __call__(self):
        while True:
            track_id = self.queue.get()
            track = self.sc_client.get("/tracks/{}".format(track_id))
            track_str = "* {} - {}\n{}\n\t{}"
            print(track_str.format(
                track.title,
                track.user['username'],
                track.description.split('\n')[0],
                track.permalink_url))
            stream_url = self.sc_client.get(track.stream_url, allow_redirects=False).location
            check_call(shlex.split("mplayer -msglevel all=-0 -really-quiet {} > /dev/null 2>&1".format(stream_url)))
