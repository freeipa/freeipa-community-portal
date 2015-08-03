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

""" Module for handling captchas in the community portal. """

from captcha.image import ImageCaptcha
from datetime import datetime, timedelta

import string
import random
import base64
import hmac
import os

from sqlalchemy import Table, Column, MetaData, String, DateTime, create_engine
from sqlalchemy.sql import select, insert, delete

import ConfigParser

Config = ConfigParser.ConfigParser()
Config.read(['/etc/freeipa_community_portal.ini', 'conf/freeipa_community_portal_dev.ini'])

KEY_LOCATION = Config.get('Captcha','key_location')
DATABASE_LOCATION = Config.get('Database', 'db_directory') + 'captcha.db'

print DATABASE_LOCATION

# retrieve the captcha key from the key file
# trust me, i know cryptography
def getKey():
    with open(KEY_LOCATION) as fp:
        return fp.read()

LENGTH = 4
KEY = getKey()

_engine = create_engine('sqlite:///' + DATABASE_LOCATION)
_metadata = MetaData()
_captcha = Table('captcha', _metadata,
    Column('hmac', String, primary_key=True),
    Column('timestamp', DateTime)
)
_metadata.create_all(_engine)

class CaptchaHelper(object):
    """Class for making a captcha for the client to display."""
    image_generator = ImageCaptcha()

    def __init__(self):
        """create a new captcha """
        # generate a captcha solution, which consists of 4 letter and digits
        self.solution = u''.join(random.SystemRandom().choice(
            (string.ascii_uppercase + string.digits).translate(None, '0OQ')) for _ in range(LENGTH)
        )

        # generate the captcha image, hold it as bytes
        self.image = self.image_generator.generate(self.solution, format='jpeg').getvalue()
        conn = _engine.connect()
        conn.execute(
            _captcha.insert().values(
                hmac=self.solution_hash(),
                timestamp=datetime.now()
            )
        )
        conn.close()
            

    def datauri(self):
        """Returns the captcha image to a data-uri, in jpeg format"""
        # convert the image bytestring to base64
        data64 = u''.join(base64.encodestring(self.image).splitlines())
        # then prepend the vital datas and return
        return u'data:{mime};base64,{data}'.format(mime='image/jpeg', data=data64)

    def solution_hash(self):
        """combines the captcha solution and a secret key into a hash that can
        be used to prove that a correct answer has been found"""
        return hmac.new(KEY, self.solution).hexdigest()

def checkResponse(response, solution):
    """Compares a given solution hash with the response provided"""
    valid = False
    digest = hmac.new(KEY, response.upper()).hexdigest()
    if hmac.compare_digest(digest, solution.encode('ascii','ignore')): 
        conn = _engine.connect()
        result = conn.execute(
            select([_captcha]).where(_captcha.c.hmac == digest)
        )
        row = result.first()
        if row is not None:
            valid = True
            conn.execute(
                delete(_captcha).where(_captcha.c.hmac==row['hmac'])
            )
        conn.close()
    return valid

