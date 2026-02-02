import datetime

class SlidingWindowRateLimiter:
    def __init__(self, capacity: int, window: datetime.timedelta):
        self.window = window
        self.capacity = capacity
        self.timestamps = []

    def acquire(self, count=1):
        self._update_timestamps()

        if len(self.timestamps) + count > self.capacity:
            count = max(self.capacity - len(self.timestamps), 0)
        for _ in range(count):
            self.timestamps.append(datetime.datetime.now())
        return count

    def get_rate(self):
        return self.capacity, self.window

    def set_rate(self, capacity=None, window=None):
        if capacity is not None:
            self.capacity = capacity
        if window is not None:
            self.window = window

    def no_capacity_for(self):
        self._update_timestamps()

        if self.capacity <= 0:
            return self.window
        if len(self.timestamps) < self.capacity:
            return datetime.timedelta(seconds=0)
        return self.window - (datetime.datetime.now() - self.timestamps[0])

    def _update_timestamps(self):
        now = datetime.datetime.now()
        self.timestamps = [ts for ts in self.timestamps if now - ts <= self.window]
        
