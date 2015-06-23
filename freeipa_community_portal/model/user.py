""" User model """
from ipalib import api, errors

class User(object): # pylint: disable=too-few-public-methods
    """ User model

    Represents a user inside of the community portal, and contains code to
    commit changes to the ipa server
    """
    def __init__(self, args=None):
        """ Takes a dictionary of attributes to assign to the user """
        if args is None:
            args = {}
        self.given_name = args.get("given_name", "")
        self.family_name = args.get("family_name", "")
        self.username = args.get("username", "")
        if not self.username and self.given_name:
            # if the username is blank, set it to a default
            self.username = self.given_name[0] + self.family_name
        self.email = args.get("email", "")

    def save(self):
        """Save the model

        This method saves the newly constructed user to the backing store. If
        the model is invalid, the model will not be saved

        If there are validation errors, returns the error message. Otherwise
        returns None
        """
        error = None
        try:
            self._call_api()
        except (errors.ValidationError, errors.RequirementError, errors.DuplicateEntry) as err:
            error = err.msg
        return error

    def _call_api(self):
        """performs the actual API call. seperate method for testing purposes
        """
        api.Command.user_add( # pylint: disable=no-member
            givenname=self.given_name,
            sn=self.family_name,
            uid=self.username,
            mail=self.email
        )
