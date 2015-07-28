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

""" Contains the base class for sending mail """
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
import ConfigParser

from jinja2 import Environment, PackageLoader

# development defaults
defaults = {
    "smtp_server": "smtp.corp.redhat.com",
    "smtp_use_auth": "False",
    "smtp_username": "",
    "smtp_password": "",
    "default_from_email": "derny@redhat.com",
    "default_admin_email": "derny@redhat.com"
}    

# first, read in the configuration file
Config = ConfigParser.ConfigParser()
# TODO: add the a read from files
files = Config.read('/etc/freeipa_community_portal.ini')

if files:
    MAIL_SERVER = Config.get("Mailers","smtp_server")
    SMTP_PORT = Config.getint("Mailers","smtp_port")
    SMTP_SEC_TYPE = Config.get("Mailers","smtp_security_type")
    DEFAULT_TO = Config.get("Mailers","default_admin_email")
    DEFAULT_FROM = Config.get("Mailers","default_from_email")
    USE_AUTH = Config.getboolean("Mailers","smtp_use_auth")
    SMTP_USERNAME = Config.get("Mailers","smtp_username")
    SMTP_PASSWORD = Config.get("Mailers","smtp_password")
else:
    MAIL_SERVER = defaults["smtp_server"]
    SMTP_PORT = 25
    SMTP_SEC_TYPE = ""
    DEFAULT_TO = defaults["default_admin_email"]
    DEFAULT_FROM = defaults["default_from_email"]
    USE_AUTH = False
    SMTP_USERNAME = ""
    SMTP_PASSWORD = ""

class Mailer(object):
    """ Base class for sending mail """
    env = Environment(loader=PackageLoader('freeipa_community_portal.mailers','templates'))

    def __init__(self):
        self.subject = "FreeIPA Community Portal: Notice"
        self.template = 'default.txt'
        # TODO: fix this
        self.to = DEFAULT_TO
        # TODO: fix this
        self.frm = DEFAULT_FROM
        self.template_opts = {}

    def mail(self):
        """Send the mail"""
        contents = self._build(self.template, self.template_opts)
        self._send(contents)

    def _build(self, template, template_opts):
        msg = MIMEMultipart()
        # TODO: change this to be configurable
        msg['From'] = self.frm
        msg['To'] = self.to
        msg['Subject'] = self.subject
        body = self.env.get_template(template).render(template_opts)
        msg.attach(MIMEText(body, 'plain'))
        return msg

    def _send(self, contents):
        if SMTP_SEC_TYPE == "SSL":
            server = smtplib.SMTP_SSL(MAIL_SERVER, SMTP_PORT)
        elif SMTP_SEC_TYPE == "STARTTLS":
            # The print statements in this function are useful for debugging
            server = smtplib.SMTP(MAIL_SERVER, SMTP_PORT)
            # print "server object created"
            server.starttls();
        else:
            server = smtplib.SMTP(MAIL_SERVER, SMTP_PORT)

        if USE_AUTH:
            server.login(SMTP_USERNAME,SMTP_PASSWORD)
        # print "tls started"
        server.sendmail(contents['From'], contents['To'], contents.as_string())
        # print "mail sent"
        # print contents
