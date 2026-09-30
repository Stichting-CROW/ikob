import pytest

from ikob.id_store import ZoneIdStoreSingleton


@pytest.fixture(autouse=True)
def clear_zone_id_store_singleton():
    """Ensure the singleton is reset after every test case."""
    ZoneIdStoreSingleton.clear_instance()
    yield  # Code after yield is run after a test run
    ZoneIdStoreSingleton.clear_instance()
