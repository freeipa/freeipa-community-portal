import pytest
from freeipa_community_portal import app

@pytest.fixture
def webapp():
    return app.SelfServicePortal()

def test_index(webapp):
    assert webapp.index() == "Hello, World!"
