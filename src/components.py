class LazyValue:
    def __init__(self, f, *args):
        self.f = f
        self.args = args
        self.value = None

    def __call__(self):
        if self.value is None:
            self.value = self.f(*self.args)
        return self.value


class Components:
    components = {}

    def find(self, name):
        return self.components[name]()

    def append(self, component):
        self.components[component.get_name()] = LazyValue(component.create, self)
        return self

    def start(self):
        for component in self.components:
            self.components[component]()
        

class A:
    @staticmethod
    def get_name():
        return 'component-A'

    @staticmethod
    def create(components):
        print('start A')
        return A()

    def print_name(self):
        print(self.get_name())


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
        self.a.print_name()


if __name__ == '__main__':
    components = Components()
    components.append(B).append(A).start()

    components.find('component-B').action()
