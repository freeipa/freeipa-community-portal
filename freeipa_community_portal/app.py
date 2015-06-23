"""
The main web server for the FreeIPA community portal.
"""

import cherrypy
import jinja2

from freeipa_community_portal.mailers.sign_up_mailer import SignUpMailer
from freeipa_community_portal.model.user import User

TEMPLATE_ENV = jinja2.Environment(loader=jinja2.FileSystemLoader('templates'))

class SelfServicePortal(object):
    """ The class for all bare pages which don't require REST logic """
    @cherrypy.expose
    def index(self):
        """/index"""
        return "Hello, World!"

    @cherrypy.expose
    def complete(self):
        """/complete"""
        return TEMPLATE_ENV.get_template('complete.html').render()

class SelfServiceUserRegistration(object):
    """Class for self-service user registration, which requires REST features"""
    exposed = True

    def GET(self):
        """GET /user"""
        return self._render_registration_form()

    def POST(self, **kwargs):
        """POST /user"""
        user = User(kwargs)
        errors = user.save()
        if not errors:
            # email the admin that the user has signed up
            SignUpMailer(user).mail()
            raise cherrypy.HTTPRedirect('/complete')
        return self._render_registration_form(user, errors)

    def _render_registration_form(self, user=User(), errors=None):
        return TEMPLATE_ENV \
            .get_template('new_user.html') \
            .render(user=user, errors=errors)

if __name__ == "__main__":
    conf = {
        '/user': {
            'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
            'tools.response_headers.on': True,
            # 'tools.response_headers.headers': [('Content-Type', 'text/plain')]
        }
    }

    webapp = SelfServicePortal()
    webapp.user = SelfServiceUserRegistration()
    cherrypy.quickstart(webapp, '/', conf)
