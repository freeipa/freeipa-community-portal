import pytest
from freeipa_community_portal import app

@pytest.fixture
def webapp():
    return app.SelfServicePortal()

def test_index(webapp):
    assert webapp.index() == "Hello, World!"

@pytest.fixture
def user_reg(monkeypatch):
    def stub_render_registration_form(self, user=None, errors=None):
        return (user, errors)
    monkeypatch.setattr(
        app.SelfServiceUserRegistration, 
        '_render_registration_form',
        stub_render_registration_form
    )
    return app.SelfServiceUserRegistration()
    
class TestSelfServiceUserRegistration():

    def test_GET(self, user_reg):
        assert user_reg.GET() == (None, None)

