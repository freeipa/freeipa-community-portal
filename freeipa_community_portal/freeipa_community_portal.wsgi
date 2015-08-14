#!/usr/bin/python

import cherrypy
from freeipa_community_portal import app

application = cherrypy.Application(app.app(), script_name=None, config=app.conf)
