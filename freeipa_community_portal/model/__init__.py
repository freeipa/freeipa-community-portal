"""
This module contains all of the models for the community portal.

Models in this app are backed by and interact with the freeipa server using
ipalib. they should be the sole holders of the ipalib dependency
"""
from ipalib import api

api.bootstrap(context='cli')
api.finalize()
api.Backend.rpcclient.connect() # pylint: disable=no-member
