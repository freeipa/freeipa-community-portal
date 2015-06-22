import cherrypy
import jinja2

from mailers.sign_up_mailer import SignUpMailer
from model.user import User

template_env = jinja2.Environment(loader=jinja2.FileSystemLoader('templates'))

class SelfServicePortal(object):
    @cherrypy.expose
    def index(self):
        return "Hello, World!"

    @cherrypy.expose
    def complete(self):
        return template_env.get_template('complete.html').render()

class SelfServiceUserRegistration(object):
    exposed = True

    def GET(self):
        return self.render_registration_form()

    def POST(self, **kwargs):
        user = User(kwargs)
        errors = user.save()
        if not errors:
            # email the admin that the user has signed up
            SignUpMailer(user).mail()
            raise cherrypy.HTTPRedirect('/complete')
        return self.render_registration_form(user, errors)

    def render_registration_form(self, user=User(), errors=None):
        return template_env \
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
