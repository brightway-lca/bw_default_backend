import pytest
import bw_default_backend as backend


@pytest.fixture(autouse=True)
def reset_config():
    backend.config.__reset__()
