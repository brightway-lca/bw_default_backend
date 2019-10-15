import pytest
import bw_default_backend as backend


@pytest.fixture(autouse=True)
def reset_config():
    backend.register_backend()
    backend.config.__reset__()
