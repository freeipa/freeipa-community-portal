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

"""
This module contains all of the models for the community portal.

Models in this app are backed by and interact with the freeipa server using
ipalib. they should be the sole holders of the ipalib dependency
"""
import os

from ipalib import api

from ..config import config


def api_connect():
    """Initialize and connect to FreeIPA's RPC server.
    """
    # delay initialization of API for pre-forking web servers
    if not api.isdone('bootstrap'):
        # set client keytab env var for authentication
        keytab = config.client_keytab
        if keytab is not None:
            os.environ['KRB5_CLIENT_KTNAME'] = keytab
        ccname = config.ccache_name
        if ccname is not None:
            os.environ['KRB5CCNAME'] = ccname

        api.bootstrap(context='cli')
        api.finalize()

    if not api.Backend.rpcclient.isconnected():
        api.Backend.rpcclient.connect()
