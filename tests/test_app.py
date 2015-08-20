import pytest
from freeipa_community_portal import app
import cherrypy


@pytest.fixture
def webapp():
    return app.SelfServicePortal()


def test_index(webapp):
    assert webapp.index() == "Hello, World!"


@pytest.fixture
def user_reg(monkeypatch):
    # what the crap is this even
    # you know this has too many dependencies cause we mock them all out

    def stub_render_registration_form(self, user=None, errors=None):
        return errors

    monkeypatch.setattr(
        app.SelfServiceUserRegistration,
        '_render_registration_form',
        stub_render_registration_form
    )

    class mock_mailer():

        def __init__(self, user):
            pass

        def mail(self):
            pass

    monkeypatch.setattr(
        app,
        'SignUpMailer',
        mock_mailer
    )

    class mock_user():

        def __init__(self, args):
            pass

        def save(self):
            pass

    monkeypatch.setattr(
        app,
        'User',
        mock_user
    )

    return app.SelfServiceUserRegistration()


class TestSelfServiceUserRegistration():

    def test_GET(self, user_reg):
        assert user_reg.GET() == None

    def test_POST_valid(self, user_reg):
        with pytest.raises(cherrypy.HTTPRedirect):
            user_reg.POST()

    def test_POST_invalid(self, user_reg, monkeypatch):
        monkeypatch.setattr(
            app.User,
            'save',
            lambda self: "error"
        )

        assert user_reg.POST() == "error"
