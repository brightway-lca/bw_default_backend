import tempfile
import shutil
import pytest
try:
    from bw_default_backend import config
except ImportError:
    print("Problem import default backend")
    raise


@pytest.fixture(scope="function")
def temp_project_dir():
    """Set config to a temporary directory"""
    td = tempfile.mkdtemp()
    config.activate(td)
    yield config
    if config.dirpath:
        config.deactivate()
    shutil.rmtree(td)
