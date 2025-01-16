from components import Components


class A:
    name = 'component-A'

    @staticmethod
    def create(components, settings):
        self = A()
        self.value = settings.get('value', 'A')
        return self

    def get(self):
        return self.value


class B:
    name = 'component-B'

    @staticmethod
    def create(components, settings):
        self = B()
        self.a = components.find(A)
        return self

    def action(self):
        return self.a.get()

    def get(self):
        return False


def test_components_connection():
    components = Components({'component-A': {}, 'component-B': {}})
    components.append(B).append(A).start()

    assert components.find(B).action() == 'A'


def test_components_settings():
    components = Components({'component-A': {'value': 'C'}, 
                             'component-B': {'value': 'B'}})
    components.append(B).append(A).start()

    assert components.find(B).action() == 'C'

