import datetime

class SlidingWindowRateLimiter:
    def __init__(self, window_duration, rate):
        self.window_duration = window_duration
        self.rate = rate
        self.timestamps = []

    def accept(self, count=1):
        now = datetime.datetime.now()
        self.timestamps = [ts for ts in self.timestamps if now - ts <= self.window_duration]
        if (len(self.timestamps) + count > self.rate):
            count = max(self.rate - len(self.timestamps), 0)
        for _ in range(count):
            self.timestamps.append(now)
        return count
