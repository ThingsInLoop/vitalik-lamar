import inspect
import logging

from utils import LazyValue


class Components:
    def __init__(self, config):
        self.components = {}
        self.dependencies_map = {}
        self.config = config


    def find(self, component):
        assert component.name in self.components, f'Component {component.name} isn\'t ' \
                                                  f'appended to components'

        assert self.config[component.name].get('enabled', True), \
                   f'Component {component.name} is disabled by config'

        upper_frame = inspect.stack()[1].frame
        dependent = 'outer-world'
        if 'self' in upper_frame.f_locals:
            dependent = inspect.stack()[1].frame.f_locals['self'].__class__.name
        dependencies = self.dependencies_map.get(dependent, set())
        dependencies.add(component.name)
        self.dependencies_map[dependent] = dependencies
        
        return self.components[component.name]()


    def append(self, component):
        assert component.name in self.config, f'Component {component.name} isn\'t ' \
                                              f'declared in config'

        def logged_create(create, components, config):
            component = create(components, config)
            logging.debug(f'Start {component.name} component')
            return component

        self.components[component.name] = LazyValue(logged_create,
                                                      component.create,
                                                      self,
                                                      self.config[component.name])
        return self


    def start(self):
        for component_name in self.components:
            if not self.config[component_name].get('enabled', True):
                continue

            self.components[component_name]()
            dependencies = self.dependencies_map.get(component_name, set())
            self.dependencies_map[component_name] = dependencies


    def draw(self):
        print('flowchart TD')
        for name, _ in self.dependencies_map.items():
            print(f'    {name};')
        for name, dependencies in self.dependencies_map.items():
            for dependency in dependencies:
                print(f'    {dependency} --> {name};')
