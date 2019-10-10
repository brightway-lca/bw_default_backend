from . import config, label_mapping
from .errors import NoActiveProject
import wrapt


@wrapt.decorator
def has_project(wrapped, instance, args, kwargs):
    if not config.project:
        raise NoActiveProject
    return wrapped(*args, **kwargs)


@has_project
def reset_database():
    """Delete all database content.

    Used in testing, as default project creation creates some basic metadata."""
    for table in reversed(list(label_mapping.values())):
        table.delete().execute()
