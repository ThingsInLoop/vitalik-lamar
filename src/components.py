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
        
