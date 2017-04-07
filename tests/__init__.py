import tempfile
import shutil
import pytest
from bw_default_backend import config


@pytest.fixture(scope="function")
def temp_project_dir():
    """Set config to a temporary directory"""
    td = tempfile.mkdtemp()
    config.activate(td)
    yield config
    if config.dirpath:
        config.deactivate()
    shutil.rmtree(td)
