import json
import logging
import os
from memory.memory_path import KNOWN_NODES_DIR

from core.node import Node


class KnownNodesMemory:
    def __init__(self):
        self.known_nodes_file = KNOWN_NODES_DIR

    def store_known_nodes(self, known_nodes: list):
        logging.info("Store known nodes")
        with open(self.known_nodes_file, "w") as jsonFile:
            json.dump(known_nodes, jsonFile, indent=2)

    @property
    def known_nodes(self) -> [Node]:
        with open(self.known_nodes_file) as f:
            nodes = json.load(f)
            known_nodes = [Node(hostname=node["hostname"]) for node in nodes]
        return known_nodes

    def store_new_node(self, new_node: Node):
        logging.info(f"Storing new node: {new_node.hostname}")
        with open(self.known_nodes_file, "r+") as f:
            current_nodes_json = json.load(f)
            current_nodes = [Node(hostname=node["hostname"]) for node in current_nodes_json]
            if new_node not in current_nodes:
                current_nodes_json.append(new_node.dict)
                f.seek(0)
                json.dump(current_nodes_json, f, indent=2)

    def store_nodes(self, nodes: [Node]):
        for node in nodes:
            self.store_new_node(node)

    def return_known_nodes(self) -> []:
        with open(self.known_nodes_file) as f:
            current_nodes_json = json.load(f)
        return current_nodes_json
