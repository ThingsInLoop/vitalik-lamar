import utils
import datetime
import time

def test_sliding_window_rate_limiter():
    rate_limiter = utils.SlidingWindowRateLimiter(datetime.timedelta(milliseconds=100), 5)

    assert rate_limiter.acquire() == 1
    assert rate_limiter.acquire() == 1
    assert rate_limiter.acquire() == 1
    
    time.sleep(0.05)
    assert rate_limiter.no_capacity_for() == datetime.timedelta(seconds=0)
    assert rate_limiter.acquire() == 1
    assert rate_limiter.acquire() == 1
    assert rate_limiter.acquire() == 0
    assert rate_limiter.no_capacity_for() > datetime.timedelta(seconds=0)

    time.sleep(0.06)
    assert rate_limiter.acquire() == 1
    assert rate_limiter.acquire() == 1
    assert rate_limiter.acquire() == 1
    assert rate_limiter.acquire() == 0


def test_sliding_window_rate_limiter2():
    rate_limiter = utils.SlidingWindowRateLimiter(datetime.timedelta(milliseconds=10), 5)

    assert rate_limiter.acquire(5) == 5
    assert rate_limiter.acquire() == 0
    
    time.sleep(0.02)
    assert rate_limiter.acquire(7) == 5
    assert rate_limiter.acquire() == 0


def test_sliding_window_rate_limiter_settings():
    rate_limiter = utils.SlidingWindowRateLimiter(datetime.timedelta(milliseconds=100), 5)

    rate, window = rate_limiter.get_rate()
    assert rate == 5
    assert window == datetime.timedelta(milliseconds=100)

    rate_limiter.set_rate(1, datetime.timedelta(seconds=60))
    rate, window = rate_limiter.get_rate()
    assert rate == 1
    assert window == datetime.timedelta(seconds=60)
