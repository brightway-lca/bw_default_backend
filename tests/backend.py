from . import temp_project_dir
from bw_default_backend import config, Collection, Method
import os
import pytest


def test_basic_setup(temp_project_dir):
    assert config.dirpath
    assert "db" in os.listdir(config.dirpath)
    assert Collection.select().count() == 0
    assert Method.select().count() == 0

def test_deactivation(temp_project_dir):
    config.deactivate()
    assert not config.dirpath
    with pytest.raises(TypeError):
        Collection.select().count()
