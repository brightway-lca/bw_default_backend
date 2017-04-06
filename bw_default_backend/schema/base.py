from ..errors import WrongDatabase
from ..peewee import database
from copy import deepcopy
from peewee import Model


class ProjectAwareModel(Model):
    def __init__(self, *args, **kwargs):
        from .. import config
        super().__init__(*args, **kwargs)
        self.__dirpath = deepcopy(config.dirpath)

    def save(self, *args, **kwargs):
        from .. import config
        if config.dirpath != self.__dirpath:
            raise WrongDatabase
        super().save(*args, **kwargs)

    def delete_instance(self, *args, **kwargs):
        from .. import config
        if config.dirpath != self.__dirpath:
            raise WrongDatabase
        super().delete_instance(*args, **kwargs)

    class Meta:
        database = database

