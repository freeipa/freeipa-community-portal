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
# import smtplib

from jinja2 import Environment, PackageLoader

class Mailer(object):
    """ Base class for sending mail """
    env = Environment(loader=PackageLoader('freeipa_community_portal.mailers','templates'))

    def __init__(self):
        self.subject = "FreeIPA Community Portal: Notice"
        self.template = 'default.txt'
        self.template_opts = {}

    def mail(self):
        """Send the mail"""
        contents = self._build(self.template, self.template_opts)
        self._send(contents)

    def _build(self, template, template_opts):
        msg = MIMEMultipart()
        # TODO: change this to be configurable
        msg['From'] = 'derny@redhat.com'
        msg['To'] = 'derny@redhat.com'
        msg['Subject'] = self.subject
        body = self.env.get_template(template).render(template_opts)
        msg.attach(MIMEText(body, 'plain'))
        return msg

    def _send(self, contents):
        # TODO: Actually send email
        print contents
