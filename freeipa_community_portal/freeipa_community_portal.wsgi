#!/usr/bin/python

import cherrypy
from freeipa_community_portal import app
from freeipa_community_portal.config import config

config.load(config.deployment_config)

application = cherrypy.Application(
    app.app(),
    script_name=None,
    config=app.conf
)
