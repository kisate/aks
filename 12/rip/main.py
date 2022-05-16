import json
from unicodedata import name
from node import Node

from threading import Thread, RLock

if __name__ == '__main__':
    schema = json.load(open('network.json'))

    lock = RLock()

    network = {
        name: Node(name, schema[name], lock)
        for name in schema
    }

    threads = [
        Thread(target=node.run, args=[network]) for node in network.values()
    ]

    for thread in threads:
        thread.start()

    changed = True
    while changed:
        changed = False
        lock.acquire()
        for node in network.values():
            changed |= node.changed
        lock.release()

    

    for node in network.values():
        node.stop()
    for thread in threads:
        thread.join()

