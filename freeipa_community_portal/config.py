# Authors:
#   Christian Heimes <cheimes@redhat.com>
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

import ConfigParser
import os


class Config(object):
    default_configs = [
        '/etc/freeipa_community_portal.ini',
        'conf/freeipa_community_portal_dev.ini'
    ]

    captcha_length = 4

    def __init__(self, *configs):
        if not configs:
            configs = self.default_configs
        self._cfg = ConfigParser.SafeConfigParser()
        print configs
        self._cfg.read(configs)
        self._captcha_key = None

    @property
    def captcha_db(self):
        return os.path.join(self._cfg.get('Database', 'db_directory'),
                            'captcha.db')

    @property
    def captcha_key_location(self):
        return self._cfg.get('Captcha', 'key_location')

    @property
    def captcha_key(self):
        if self._captcha_key is None:
            with open(self.captcha_key_location, 'rb') as f:
                self._captcha_key = f.read()
        return self._captcha_key

    @property
    def reset_db(self):
        return os.path.join(self._cfg.get('Database', 'db_directory'),
                            'resets.db')

    @property
    def smtp_server(self):
        return self._cfg.get('Mailers', 'smtp_server')

    @property
    def smtp_port(self):
        return self._cfg.getint('Mailers', 'smtp_port')

    @property
    def smtp_security_type(self):
        return self._cfg.get('Mailers', 'smtp_security_type')

    @property
    def smtp_auth(self):
        if self._cfg.getboolean('Mailers', 'smtp_use_auth'):
            return (
                self._cfg.get('Mailers', 'smtp_username'),
                self._cfg.get('Mailers', 'smtp_password')
            )
        else:
            return None

    @property
    def default_admin_email(self):
        return self._cfg.get('Mailers', 'default_admin_email')

    @property
    def default_from_email(self):
        return self._cfg.get('Mailers', 'default_from_email')


config = Config()
