import pytest
import freeipa_community_portal.model.user
from freeipa_community_portal.model.user import User
# User = freeipa_community_portal.model.user.User


def test_user_init():
    user = User()
    assert user.given_name == ""
    assert user.family_name == ""
    assert user.username == ""
    assert user.email == ""


def test_user_init_with_args_with_username():
    args = {
        "given_name": "test",
        "family_name": "user",
        "username": "testuser",
        "email": "test@example.com"
    }
    user = User(args)

    assert user.given_name == args["given_name"]
    assert user.family_name == args["family_name"]
    assert user.username == args["username"]
    assert user.email == args["email"]


def test_user_init_with_args_no_username():
    args = {
        "given_name": "test",
        "family_name": "user",
        "email": "test@example.com"
    }
    user = User(args)

    assert user.given_name == args["given_name"]
    assert user.family_name == args["family_name"]
    assert user.username == "tuser"
    assert user.email == args["email"]

# wtf am i doing


class mock_errors():
    # this seems logical

    class ValidationError(Exception):

        def __init__(self):
            self.msg = 'test_valid'

    class RequirementError(Exception):

        def __init__(self):
            self.msg = 'test_req'

    class DuplicateEntry(Exception):

        def __init__(self):
            self.msg = 'test_dup'


def test_save_no_errors(monkeypatch):
    def mock_call_api(self):
        pass
    monkeypatch.setattr(User, '_call_api', mock_call_api)
    user = User()

    assert user.save() is None


def test_save_validation_error(monkeypatch):
    def mock_call_api(self):
        raise mock_errors.ValidationError
    monkeypatch.setattr(User, '_call_api', mock_call_api)
    monkeypatch.setattr(
        freeipa_community_portal.model.user, 'errors', mock_errors)
    user = User()
    assert user.save() == 'test_valid'


def test_save_requirement_error(monkeypatch):
    def mock_call_api(self):
        raise mock_errors.RequirementError
    monkeypatch.setattr(User, '_call_api', mock_call_api)
    monkeypatch.setattr(
        freeipa_community_portal.model.user, 'errors', mock_errors)
    user = User()
    assert user.save() == 'test_req'


def test_save_requirement_error(monkeypatch):
    def mock_call_api(self):
        raise mock_errors.DuplicateEntry
    monkeypatch.setattr(User, '_call_api', mock_call_api)
    monkeypatch.setattr(
        freeipa_community_portal.model.user, 'errors', mock_errors)
    user = User()
    assert user.save() == 'test_dup'
