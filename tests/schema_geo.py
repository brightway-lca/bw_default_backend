from bw_default_backend import Geocollection, Location
from brightway_projects import projects
from brightway_projects.testing import bwtest
import datetime


def test_geocollection_modified_autoupdates(bwtest):
    projects.create_project("test", add_base_data=False)
    now = datetime.datetime.utcnow() - datetime.timedelta(minutes=1)
    Geocollection.create(name="foo", modified=now - datetime.timedelta(days=1))
    gc = Geocollection.get(name="foo")
    assert gc.modified < now

    Location.create(geocollection=gc, name="bar")
    gc = Geocollection.get(name="foo")
    assert gc.modified > now

    gc.modified = now
    gc.save()

    Location.get(name="bar").delete_instance()
    gc = Geocollection.get(name="foo")
    assert gc.modified > now


def test_geocollection_modified_autoupdates_location_moved(bwtest):
    projects.create_project("test", add_base_data=False)
    now = datetime.datetime.utcnow() - datetime.timedelta(minutes=1)
    gc = Geocollection.create(name="foo", modified=now - datetime.timedelta(days=1))
    Location.create(geocollection=gc, name="bar")
    Geocollection.create(name="baz", modified=now - datetime.timedelta(days=1))
    gc = Geocollection.get(name="foo")
    gc.modified = now - datetime.timedelta(days=1)
    gc.save()

    for obj in Geocollection.select():
        assert obj.modified < now

    l = Location.get(name="bar")
    l.geocollection = Geocollection.get(name="baz")
    l.save()

    for obj in Geocollection.select():
        assert obj.modified > now
