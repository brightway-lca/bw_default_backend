from . import temp_project_dir
from bw_default_backend import config, Collection
from bw_default_backend.errors import WrongDatabase
import os
import pytest
import shutil
import tempfile


def test_changing_config_raises_wrong_database(temp_project_dir):
    co = Collection()
    co.name = "Foo"
    co.data = {}
    co.save()
    assert co.id

    config.deactivate()
    td = tempfile.mkdtemp()
    config.activate(td)

    with pytest.raises(WrongDatabase):
        co.save()

    with pytest.raises(WrongDatabase):
        co.delete_instance()

    config.deactivate()
    shutil.rmtree(td)
