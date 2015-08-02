from pluggy import PluginManager
from . import hookspec, PROJECT_NAME


# TODO: move to main?

manager = PluginManager(PROJECT_NAME)
manager.add_hookspecs(hookspec)
manager.load_setuptools_entrypoints('gumby.plugin')
