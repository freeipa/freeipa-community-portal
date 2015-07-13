""" Module for handling captchas in the community portal. """

from captcha.image import ImageCaptcha
from datetime import datetime, timedelta

import string
import random
import base64
import hmac

from sqlalchemy import Table, Column, MetaData, String, DateTime, create_engine
from sqlalchemy.sql import select, insert, delete

LENGTH = 4
# TODO: this is not a secure key
KEY = 'lol you should probably change this'

#TODO: fix this so that it uses in-memory database
_engine = create_engine('sqlite:///captcha.db', echo=True)
_metadata = MetaData()
_captcha = Table('captcha', _metadata,
    Column('hmac', String, primary_key=True),
    Column('timestamp', DateTime)
)
_metadata.create_all(_engine)
USE_BY = timedelta(days=1)

class CaptchaHelper(object):
    """Class for making a captcha for the client to display."""
    image_generator = ImageCaptcha()

    def __init__(self):
        """create a new captcha """
        # generate a captcha solution, which consists of 4 letter and digits
        self.solution = u''.join(random.SystemRandom().choice(
            string.ascii_uppercase + string.digits) for _ in range(LENGTH)
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

