import sys
from multiprocessing import Queue, Process
from cumuliform import CumuliformGatherer, CumuliformPlayer

def run():
    client_id = sys.argv[1]
    track_queue = Queue()
    player = CumuliformPlayer(client_id, track_queue)
    proc = Process(target=player)
    proc.start()
    gatherer = CumuliformGatherer(track_queue)
    gatherer.run()
