from datetime import datetime, timedelta
import os
import base64

from sqlalchemy import Table, Column, MetaData, String, DateTime, create_engine
from sqlalchemy.sql import select, insert, delete

_engine = create_engine('sqlite:///database.db', echo=True)

_metadata = MetaData()
_password_reset = Table('password_reset', _metadata,
    Column('username', String, primary_key=True),
    Column('token', String),
    Column('timestamp', DateTime)
)

_metadata.create_all(_engine)

USE_BY = timedelta(days=3)

class PasswordReset(object):
    """Represents a password reset object"""

    def __init__(self, username):
        self.username = username
        self.token = base64.urlsafe_b64encode(os.urandom(8)).rstrip('=')
        self.timestamp = datetime.now()

    @staticmethod
    def load(username):
        """Class method. Load a password reset, if one exists.

        :param: username - the user to laod

        :return: a PasswordReset object associated with the user if one exists,
        None otherwise
        """
        # connect to the database
        conn = _engine.connect()
        # and grab a record cooresponding to this username
        result = conn.execute(
            select([_password_reset]).where(_password_reset.c.username == username)
        )

        row = result.first()
        # if there is no result, return None
        if row is None:
            reset = None
        # or the result is too old, expire the result and return None
        elif (datetime.now() - row['timestamp']) > USE_BY:
            reset = None
            PasswordReset.expire(row['username'])
        # but if the result is valid...
        else:
            reset = PasswordReset(row['username'])
            reset.token = row['token']
            reset.timestamp =  row['timestamp']

        # close our resources
        conn.close()
        return reset

    def save(self):
        conn = _engine.connect()
        self.expire(self.username)
        conn.execute(
            _password_reset.insert().values(
                username=self.username,
                token=self.token,
                timestamp = self.timestamp
            )
        )
        conn.close()

    def reset_password(self):
        """Calls the IPA API and sets the password to a new, random value"""
        return base64.urlsafe_b64encode(os.urandom(8)).rstrip('=')

    @staticmethod
    def expire(username):
        conn = _engine.connect()
        conn.execute(
            delete(_password_reset).where(_password_reset.c.username == username)
        )
        conn.close()
    
