from utils import LazyValue


class Components:
    def __init__(self, config):
        self.components = {}
        self.config = config


    def find(self, component):
        assert component.name in self.components, f'Component {component.name} isn\'t ' \
                                                  f'appended to components'

        assert self.config[component.name].get('enabled', True), \
                   f'Component {component.name} is disabled by config'

        return self.components[component.name]()


    def find_str(self, name):
        return self.components[name]()


    def append(self, component):
        assert component.name in self.config, f'Component {component.name} isn\'t ' \
                                              f'declared in config'

        self.components[component.name] = LazyValue(component.create,
                                                      self,
                                                      self.config[component.name])
        return self


    def start(self):
        print(self.components)
        for component_name in self.components:
            if not self.config[component_name].get('enabled', True):
                continue

            self.components[component_name]()
        
