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
import errno
import os

from sqlalchemy import MetaData, create_engine


class Config(object):
    development_config = ('freeipa_community_portal/conf/'
                          'freeipa_community_portal_dev.ini')
    deployment_config = '/etc/freeipa_community_portal.ini'

    captcha_length = 4
    umask = 0o027

    metadata = MetaData()

    def __init__(self):
        self._cfg = None
        self.configfile = None
        self._captcha_key = None
        self._engine = None

    def __nonzero__(self):
        return self._cfg is not None

    def load(self, configfile):
        cfg = ConfigParser.SafeConfigParser()
        with open(configfile) as f:
            cfg.readfp(f, configfile)
        self._cfg = cfg
        self.configfile = configfile
        # set secure umask
        os.umask(self.umask)
        self._init_vardir()
        self._init_captcha_key()
        self._init_engine()

    def _init_vardir(self):
        """Create our var directory with secure mode
        """
        if not os.path.isdir(self.db_directory):
            os.makedirs(self.db_directory, mode=0o750)

    def _init_captcha_key(self):
        """Read or create captcha key file
        """
        try:
            with open(self.captcha_key_location, 'rb') as f:
                self._captcha_key = f.read()
        except IOError as e:
            if e.errno != errno.ENOENT:
                raise
            new_key = os.urandom(8)
            # write key with secure mode
            with open(self.captcha_key_location, 'wb') as f:
                os.fchmod(f.fileno(), 0o600)
                f.write(new_key)
                os.fdatasync(f.fileno())
            # re-read key from file system in case somebody else wrote to it.
            with open(self.captcha_key_location, 'rb') as f:
                self._captcha_key = f.read()

    def _init_engine(self):
        """Create engine and tables
        """
        if self._engine is not None:
            self._engine.dispose()
        self._engine = create_engine('sqlite:///' + self.communityportal_db)
        self.metadata.create_all(self._engine)

    def _get_default(self, section, option, raw=False, vars=None,
                     default=None):
        try:
            return self._cfg.get(section, option, raw=raw, vars=vars)
        except (ConfigParser.NoSectionError, ConfigParser.NoOptionError):
            return default

    @property
    def engine(self):
        return self._engine

    @property
    def db_directory(self):
        return self._cfg.get('Database', 'db_directory')

    @property
    def communityportal_db(self):
        return os.path.join(self.db_directory, 'communityportal.db')

    @property
    def captcha_key_location(self):
        return os.path.join(self.db_directory, 'captcha.key')

    @property
    def captcha_key(self):
        return self._captcha_key

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

    @property
    def client_keytab(self):
        keytab = self._get_default('KRB5', 'client_keytab')
        if not keytab or not keytab.strip():
            return None
        return keytab

    @property
    def ccache_name(self):
        ccache_name = self._get_default('KRB5', 'ccache_name')
        if not ccache_name or not ccache_name.strip():
            return None
        return ccache_name


config = Config()
