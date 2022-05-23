import re
from typing import Dict
from threading import RLock

class Node:

    INF = 10000

    def __init__(self, name: str, neighbors: Dict[str, int], lock: RLock):
        self.name = name
        self.neighbors = set(neighbors.keys())
        self.vector = neighbors.copy()
        self.next_hop = {
            neighbor: neighbor
            for neighbor in self.neighbors
        }
        self.cost = neighbors.copy()
        self.lock = lock
        self.running = False
        self.changed = True

    def update_vector_with(self, key: str, new_value: int, next_hop: str):
        if new_value < Node.INF and (key not in self.vector or new_value < self.vector[key]):
            self.vector[key] = new_value
            self.next_hop[key] = next_hop
            return True
        return False

    def get_vec(self, node: str):
        if node in self.vector:
            return self.vector[node]
        return self.INF

    def print_results(self):
        print(f'{"[Source IP]":20} {"[Destination IP]":20} {"[Next Hop]":20} {"Metric":20}')
        for to_node_name in self.vector:
            distance = self.vector[to_node_name] if to_node_name in self.vector else 'inf'
            print(f'{self.name:20} {to_node_name:20} {self.next_hop[to_node_name]:20} {str(distance):20}')

    def run(self, network: Dict[str, "Node"]):
        self.running = True
        step = 1
        while self.running:
            self.lock.acquire()
            self.changed = False
            for neighbor in self.neighbors:
                next_node: Node = network[neighbor]
                for to_node, d in next_node.vector.items():
                    if to_node == self.name:
                        continue
                    if to_node in self.next_hop and self.next_hop[to_node] == neighbor and min(self.INF, d + self.cost[neighbor]) != self.get_vec(to_node):
                        del self.vector[to_node]
                        del self.next_hop[to_node]
                        self.changed = True
                    
                for to_node, d in next_node.vector.items():
                    if to_node == self.name:
                        continue

                    self.changed |= self.update_vector_with(to_node, d + self.cost[neighbor], next_node.name)
                
            if self.changed:
                print(f"Step {step} for node {self.name}")    
                self.print_results()
                print()
            step += 1
            self.lock.release()
        
        self.lock.acquire()
        print(f"Final step for node {self.name}")    
        self.print_results()
        print()
        self.lock.release()

    def stop(self):
        self.running = False