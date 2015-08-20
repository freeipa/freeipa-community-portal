# Authors:
#   Drew Erny <derny@redhat.com>
#
# Copyright (C) 2015  Red Hat
# see file 'COPYING' for use and warranty information
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""User model
"""
from ipalib import api, errors

from . import api_connect


class User(object):  # pylint: disable=too-few-public-methods
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
        self.password = args.get("password", "")
        self.password2 = args.get("password2", "")
        if not self.username and self.given_name:
            # if the username is blank, set it to a default
            self.username = self.given_name[0] + self.family_name
        self.email = args.get("email", "")

    def validate(self):
        err = []
        if not self.given_name:
            err.append('Given name is required.')
        if not self.family_name:
            err.append('Family name is required.')
        if not self.email or "@" not in self.email:
            err.append("Invalid email address.")
        if self.password != self.password2:
            err.append("Passwords mismatch.")
        elif len(self.password) < 8:
            err.append("Password too short, need 8 characters or more.")
        try:
            self.check_available()
        except errors.DuplicateEntry as exc:
            err.append(exc.msg)
        return err

    def save(self):
        """Save the model

        This method saves the newly constructed user to the backing store. If
        the model is invalid, the model will not be saved

        If there are validation errors, returns the error message. Otherwise
        returns None
        """
        err = []
        try:
            self._call_api()
        except (errors.ValidationError,
                errors.RequirementError,
                errors.DuplicateEntry) as exc:
            err.append(exc.msg)
        return err

    def check_available(self):
        """Checks if the user name is still available.

        For a better user experience, this check is done in advanced.
        """
        api_connect()
        message = 'active user with name "%(user)s" already exists' % {
            'user': self.username
        }
        # Check if the username conflicts with an existing user. The check
        # is not perfect. A user might be created before the stage user is
        # activated. The code also suffers from a race condition. It's as
        # good as it can get without a better API, though.
        # see https://fedorahosted.org/freeipa/ticket/5186
        try:
            api.Command.user_show(uid=self.username)
        except errors.NotFound:
            pass
        else:
            raise errors.DuplicateEntry(message=message)

        try:
            api.Command.stageuser_show(uid=self.username)
        except errors.NotFound:
            pass
        else:
            raise errors.DuplicateEntry(message=message)

    def _call_api(self):
        """performs the actual API call. seperate method for testing purposes
        """
        api_connect()

        api.Command.stageuser_add(  # pylint: disable=no-member
            givenname=self.given_name,
            sn=self.family_name,
            uid=self.username,
            mail=self.email,
            userpassword=self.password
        )
