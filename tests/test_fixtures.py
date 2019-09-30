from fixtures.create_fixtures import basic_fixture
from brightway.testing import bwtest, projects
from bw_default_backend import *


def test_basic_fixtures(bwtest, basic_fixture):
    assert Activity.select().count() == 2

def test_basic_fixtures_missing(bwtest):
    projects.create(name="test")
    assert Activity.select().count() == 0
