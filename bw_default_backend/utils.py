from . import config
from .errors import NoActiveProject
import wrapt


@wrapt.decorator
def has_project(wrapped, instance, args, kwargs):
    if not config.project:
        raise NoActiveProject
    return wrapped(*args, **kwargs)
