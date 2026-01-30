import utils
import datetime
import time

def test_sliding_window_rate_limiter():
    rate_limiter = utils.SlidingWindowRateLimiter(datetime.timedelta(milliseconds=100), 5)

    assert rate_limiter.accept() == 1
    assert rate_limiter.accept() == 1
    assert rate_limiter.accept() == 1
    
    time.sleep(0.05)
    assert rate_limiter.accept() == 1
    assert rate_limiter.accept() == 1
    assert rate_limiter.accept() == 0

    time.sleep(0.06)
    assert rate_limiter.accept() == 1
    assert rate_limiter.accept() == 1
    assert rate_limiter.accept() == 1
    assert rate_limiter.accept() == 0


def test_sliding_window_rate_limiter2():
    rate_limiter = utils.SlidingWindowRateLimiter(datetime.timedelta(milliseconds=10), 5)

    assert rate_limiter.accept(5) == 5
    assert rate_limiter.accept() == 0
    
    time.sleep(0.02)
    assert rate_limiter.accept(7) == 5
    assert rate_limiter.accept() == 0
