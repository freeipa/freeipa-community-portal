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

import base64
import hmac
import random
import string

from datetime import datetime

from captcha.image import ImageCaptcha

from sqlalchemy import Column, DateTime, String, Table
from sqlalchemy.sql import delete, select

from ..config import config

# retrieve the captcha key from the key file
# trust me, i know cryptography

_captcha = Table('captcha', config.metadata,
                 Column('hmac', String, primary_key=True),
                 Column('timestamp', DateTime)
                 )


class CaptchaHelper(object):
    """Class for making a captcha for the client to display.
    """
    image_generator = ImageCaptcha()

    def __init__(self):
        """create a new captcha """
        # generate a captcha solution, which consists of 4 letter and digits
        chars = string.ascii_uppercase + string.digits
        chars = chars.translate(None, '0OQ')
        systemrandom = random.SystemRandom()
        self.solution = u''.join(systemrandom.choice(chars)
                                 for _ in range(config.captcha_length))

        # generate the captcha image, hold it as bytes
        self.image = self.image_generator.generate(
            self.solution, format='jpeg').getvalue()
        conn = config.engine.connect()
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
        return u'data:{mime};base64,{data}'.format(mime='image/jpeg',
                                                   data=data64)

    def solution_hash(self):
        """combines the captcha solution and a secret key into a hash that can
        be used to prove that a correct answer has been found"""
        return hmac.new(config.captcha_key, self.solution).hexdigest()


def check_response(response, solution):
    """Compares a given solution hash with the response provided"""
    valid = False
    digest = hmac.new(config.captcha_key, response.upper()).hexdigest()
    if hmac.compare_digest(digest, solution.encode('ascii', 'ignore')):
        conn = config.engine.connect()
        result = conn.execute(
            select([_captcha]).where(_captcha.c.hmac == digest)
        )
        row = result.first()
        if row is not None:
            valid = True
            conn.execute(
                delete(_captcha).where(_captcha.c.hmac == row['hmac'])
            )
        conn.close()
    return valid
