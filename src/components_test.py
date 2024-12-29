from components import Components
from components import LazyValue


def test_lazy_value():
    lz = LazyValue(lambda x : x + 1, 1)
    assert lz() == 2
    assert lz() == 2


class A:
    @staticmethod
    def get_name():
        return 'component-A'

    @staticmethod
    def create(components):
        print('start A')
        return A()

    def get(self):
        return 'A'


class B:
    @staticmethod
    def get_name():
        return 'component-B'

    @staticmethod
    def create(components):
        print('start B')
        self = B()
        self.a = components.find('component-A')
        return self

    def action(self):
        return self.a.get()

    def get(self):
        return False


def test_components():
    components = Components()
    components.append(B).append(A).start()

    assert components.find('component-B').action() == 'A'
