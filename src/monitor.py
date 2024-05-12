import time
import json
import os


class SingletonMeta(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]


def timeit(func):
    monitor = Monitor()

    def wrap(*args, **kwargs):
        now = time.perf_counter()
        ret = func(*args, **kwargs)
        elapsed = time.perf_counter() - now
        monitor.addStatus(f"{func.__name__}", elapsed)
        return ret
    return wrap


class Monitor(metaclass=SingletonMeta):

    def __init__(self):
        self.logPath = "./log"
        self.logFile = "log.json"
        self.status = dict()

        if not os.path.exists(self.logPath):
            os.mkdir(self.logPath)

    def getStatus(self):
        return self.status

    def addStatus(self, key: str, status: dict):
        self.status[key] = str(status)
        filepath = f"{self.logPath}/{self.logFile}"
        with open(filepath, "w+") as f:
            json.dump(self.status,f)



if __name__ == "__main__":

    m1 = Monitor()
    m2 = Monitor()

    m1.addStatus("add", {"status": 0})
    assert (m1 is m2)
    assert ({"add": {"status": 0}} == m2.getStatus())
