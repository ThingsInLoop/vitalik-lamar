import utils

def test_lazy_value():
    lz = utils.LazyValue(lambda x : x + 1, 1)
    assert lz.value is None
    assert lz() == 2
    assert lz() == 2
