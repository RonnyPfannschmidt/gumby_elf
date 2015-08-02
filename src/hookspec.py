from . import PROJECT_NAME
from pluggy import HookspecMarker


hookspec = HookspecMarker(PROJECT_NAME)


@hookspec(firstresult=True)
def read_specification(root):
    """
    :param root: a path to a proejct root
    :returns: None or a configured metadata source
    """
    pass
