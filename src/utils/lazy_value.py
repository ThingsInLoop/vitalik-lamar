class LazyValue:
    def __init__(self, f, *args):
        self.f = f 
        self.args = args
        self.value = None

    def __call__(self):
        if self.value is None:
            self.value = self.f(*self.args)
        return self.value

