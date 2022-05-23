import json
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

    print("Changing 0--3 to 1")

    lock.acquire()

    network["0"].cost["3"] = 1
    network["0"].vector["3"] = 1
    network["0"].next_hop["3"] = "3"
    network["3"].cost["0"] = 1
    network["3"].vector["0"] = 1
    network["3"].next_hop["0"] = "0"

    print("Changing 2--1 to 5")

    network["1"].cost["2"] = 5
    network["1"].vector["2"] = 5
    network["1"].next_hop["2"] = "2"
    network["2"].cost["1"] = 5
    network["2"].vector["1"] = 5
    network["2"].next_hop["1"] = "1"

    lock.release()

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



