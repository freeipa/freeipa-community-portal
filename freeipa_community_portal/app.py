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
The main web server for the FreeIPA community portal.
"""

import os

import cherrypy

import jinja2

from freeipa_community_portal import PACKAGE_DATA_DIR
from freeipa_community_portal.config import config
from freeipa_community_portal.mailers.reset_password_mailer import ResetPasswordMailer
from freeipa_community_portal.mailers.sign_up_mailer import SignUpMailer
from freeipa_community_portal.model.captcha_wrapper import (
    CaptchaHelper, check_response)
from freeipa_community_portal.model.password_reset import PasswordReset
from freeipa_community_portal.model.user import User


TEMPLATE_ENV = jinja2.Environment(
    loader=jinja2.PackageLoader('freeipa_community_portal', 'templates'))


class SelfServicePortal(object):
    """The class for all bare pages which don't require REST logic
    """

    @cherrypy.expose
    def index(self):  # pylint: disable=no-self-use
        """/index"""
        return render("layout.html")

    @cherrypy.expose
    def complete(self):  # pylint: disable=no-self-use
        """/complete"""
        # pylint: disable=no-member
        return render('complete.html')


class SelfServiceUserRegistration(object):
    """Class for self-service user registration, which requires REST features
    """
    exposed = True

    def GET(self):  # pylint: disable=invalid-name
        """GET /user"""
        return self._render_registration_form()

    def POST(self, **kwargs):  # pylint: disable=invalid-name
        """POST /user"""
        user = User(kwargs)
        errors = check_captcha(kwargs)
        if not errors:
            errors = user.save()
        if not errors:
            # email the admin that the user has signed up
            SignUpMailer(user).mail()
            raise cherrypy.HTTPRedirect('/complete')
        return self._render_registration_form(user, errors)

    def _render_registration_form(self, user=User(), errors=None):  # pylint: disable=no-self-use
        """renders the registration form. private."""
        # pylint: disable=no-member
        captcha = CaptchaHelper()

        return render('new_user.html', user=user, errors=errors, captcha=captcha)


class RequestSelfServicePasswordReset(object):
    """Handles requesting a password reset

    GET, POST /request_reset
    """
    exposed = True

    def GET(self):
        """returns the request form"""
        captcha = CaptchaHelper()
        return render('request_reset.html', captcha=captcha)

    def POST(self, **kwargs):
        """accepts a username and initiates a reset"""
        errors = check_captcha(kwargs)
        if not errors and not kwargs['username']:
            errors = "Username is required"
        if errors:
            return render('request_reset.html', errors=errors, captcha=CaptchaHelper())
        r = PasswordReset(kwargs['username'])
        r.save()
        if r.check_valid():
            ResetPasswordMailer(r).mail()
        raise cherrypy.HTTPRedirect('/complete')


class SelfServicePasswordReset(object):
    """Handles the actual reset of the password

    GET, POST /reset_password
    """
    exposed = True

    def GET(self, **params):
        """Renders the reset request form.

        if username and/or token are supplied in the querystring, pre-fills the
        form for the user
        """
        username = params.get('username', '')
        token = params.get('token', '')
        return render('reset_password.html', username=username, token=token)

    def POST(self, **params):
        if 'username' not in params or 'token' not in params:
            return render('reset_password.html',
                          username=params.get('username', ''),
                          token=params.get('token', ''),
                          error='All fields are required'
                          )
        else:
            p = PasswordReset.load(params['username'])
            if p is not None and p.token == params['token']:
                new_pass = p.reset_password()
                PasswordReset.expire(params['username'])
                return render('display_password.html', password=new_pass)
            else:
                PasswordReset.expire(params['username'])
                return render('invalid_token.html')


def render(template, **args):
    return TEMPLATE_ENV.get_template(template).render(**args)


def check_captcha(args):
    if not check_response(args['response'], args['solution']):
        return "Incorrect Captcha response"
    else:
        return None


conf = {
    '/assets': {
        'tools.staticdir.on': True,
        'tools.staticdir.dir': os.path.join(PACKAGE_DATA_DIR, 'assets'),
    },
    '/user': {
        'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
        'tools.response_headers.on': True,
        # 'tools.response_headers.headers': [('Content-Type', 'text/plain')]
    },
    '/request_reset': {
        'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
        'tools.response_headers.on': True,
    },
    '/reset_password': {
        'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
        'tools.response_headers.on': True,
    }
}


def app():
    """Main entry point for the web application. If you run this library as a
    standalone application, you can just use this function
    """
    if not config:
        raise ValueError('Run config.load(configfile) first!')

    webapp = SelfServicePortal()
    webapp.user = SelfServiceUserRegistration(
    )  # pylint: disable=attribute-defined-outside-init
    webapp.request_reset = RequestSelfServicePasswordReset()
    webapp.reset_password = SelfServicePasswordReset()
    return webapp
