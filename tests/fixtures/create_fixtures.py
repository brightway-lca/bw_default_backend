import brightway_projects as bw
import bw_default_backend as backend
import pytest


@pytest.fixture(scope="function")
def basic_fixture():
    NAME = "test-fixtures"
    # if NAME in bw.projects:
    #     bw.projects.delete_project(NAME)
    bw.projects.create_project(NAME)

    backend.reset_database()

    biosphere_collection = backend.Collection.create(name="biosphere")
    food_collection = backend.Collection.create(name="food")

    first = backend.Flow.create(
        name="an emission", kind="biosphere", collection=biosphere_collection, unit="kg"
    )
    second = backend.Flow.create(
        name="another emission",
        kind="biosphere",
        collection=biosphere_collection,
        unit="kg",
    )
    world = backend.Geocollection.create(name="world")
    canada = backend.Location.create(geocollection=world, name="Canada")
    lunch_flow = backend.Flow.create(
        name="lunch food", unit="kg", kind="technosphere", collection=food_collection
    )
    lunch_activity = backend.Activity.create(
        name="eating lunch",
        collection=food_collection,
        reference_product=lunch_flow,
        location=canada,
    )
    backend.Exchange.create(
        activity=lunch_activity, flow=lunch_flow, direction="production", amount=0.5
    )
    backend.Exchange.create(activity=lunch_activity, flow=first, amount=0.05)
    dinner_flow = backend.Flow.create(
        name="dinner main dish",
        unit="kg",
        kind="technosphere",
        collection=food_collection,
    )
    dinner_activity = backend.Activity.create(
        name="eating dinner",
        collection=food_collection,
        reference_product=dinner_flow,
        location=canada,
    )
    backend.Exchange.create(
        activity=dinner_activity, flow=dinner_flow, direction="production", amount=0.25
    )
    backend.Exchange.create(activity=dinner_activity, flow=second, amount=0.15)
