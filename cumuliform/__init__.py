import sys
from multiprocessing import Queue, Process
from cumuliform import CumuliformGatherer, CumuliformPlayer


def run():
    client_id = sys.argv[1]
    track_queue = Queue()
    player = CumuliformPlayer(track_queue, client_id)
    proc = Process(target=player)
    proc.start()
    gatherer = CumuliformGatherer(track_queue)
    gatherer.run()
