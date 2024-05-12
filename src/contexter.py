import os
import json


class Contexter:

    def __init__(self):
        self.path_to_memory = "./memory"
        self.storageLen = 10
        self.key = dict()

        if not os.path.exists(self.path_to_memory):
            os.mkdir(self.path_to_memory)
        pass

    def memorise(self, filename, payload):
        filepath = f"{self.path_to_memory}/{filename}"
        if filename in self.key.keys():
            self.key[filename] += 1
        else:
            self.key[filename] = 0

        if not os.path.exists(filepath):
            data = []
        elif os.path.getsize(filepath) == 0:
            data = []
        else:
            with open(filepath, "r") as f:
                data = json.load(f)

        data.append(payload)
        if len(data) >= self.storageLen:
            data = data[1:]

        with open(filepath, "w") as f:
            json.dump(data, f, indent=4)

    def recall(self, filename):
        filepath = f"{self.path_to_memory}/{filename}"
        if os.path.exists(filepath):
            with open(filepath, "r") as f:
                data = json.load(f)
        else:
            data = []

        return data
