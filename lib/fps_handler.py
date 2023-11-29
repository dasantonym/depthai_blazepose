import time


class FPSHandler:
    def __init__(self):
        self.timestamp = time.time()
        self.start = time.time()
        self.frame_cnt = 0

    def next_iter(self):
        if self.frame_cnt == 50:
            self.start = self.timestamp
            self.frame_cnt = 0
        self.timestamp = time.time()
        self.frame_cnt += 1

    def fps(self):
        return self.frame_cnt / (self.timestamp - self.start)
