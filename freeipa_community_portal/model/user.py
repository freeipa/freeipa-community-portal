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
        except (errors.ValidationError,
                errors.RequirementError,
                errors.DuplicateEntry) as err:
            error = err.msg
        return error

    def _call_api(self):
        """performs the actual API call. seperate method for testing purposes
        """
        api_connect()

        api.Command.stageuser_add(  # pylint: disable=no-member
            givenname=self.given_name,
            sn=self.family_name,
            uid=self.username,
            mail=self.email
        )
