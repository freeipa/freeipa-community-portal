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
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from jinja2 import Environment, PackageLoader

from ..config import config


class Mailer(object):

    """ Base class for sending mail """
    env = Environment(
        loader=PackageLoader('freeipa_community_portal.mailers', 'templates'))

    def __init__(self):
        self.subject = "FreeIPA Community Portal: Notice"
        self.template = 'default.txt'
        self.to = config.default_admin_email
        self.frm = config.default_from_email
        self.template_opts = {}

    def mail(self):
        """Send the mail"""
        contents = self._build(self.template, self.template_opts)
        self._send(contents)

    def _build(self, template, template_opts):
        msg = MIMEMultipart()
        msg['From'] = self.frm
        msg['To'] = self.to
        msg['Subject'] = self.subject
        body = self.env.get_template(template).render(template_opts)
        msg.attach(MIMEText(body, 'plain'))
        return msg

    def _send(self, contents):
        if config.smtp_security_type == "SSL":
            smtp_cls = smtplib.SMTP_SSL
        else:
            smtp_cls = smtplib.SMTP

        server = smtp_cls(config.smtp_server, config.smtp_port)
        if config.smtp_security_type == "STARTTLS":
            server.starttls()

        auth = config.smtp_auth
        if auth is not None:
            server.login(*auth)
        # print "tls started"
        server.sendmail(contents['From'], contents['To'], contents.as_string())
        # print "mail sent"
        # print contents
