import os
import hashlib
import hmac
import uuid
from datetime import datetime

import constants
from db_base import db_base
from db_base import queue_item
from db_base import queue_cmd
from db_base import simple_sqlsafe_str


class accounts(db_base):

    def __init__(self, is_test=False):
        if is_test:
            super().__init__("accounts_test")
        else:
            super().__init__("accounts")

        self.active_sessions = sessions()
        self.login_attempts = {'name': 'last_attempt'}
        # start > datetime.now() - timedelta(seconds=10)

        cmd = "CREATE TABLE IF NOT EXISTS accounts "
        cmd += "(name TEXT PRIMARY KEY NOT NULL)"
        self.queue_command(queue_item(queue_cmd(cmd)))

        self.add_col("accounts", "pwhash", "BLOB")
        self.add_col("accounts", "pwsalt", "BLOB")

        cmd = "CREATE TABLE IF NOT EXISTS data "
        cmd += "(name TEXT, FOREIGN KEY(name) REFERENCES accounts(name))"
        self.queue_command(queue_item(queue_cmd(cmd)))

        # Add whatever cols have been specified in constants
        for col in constants.db_col_names:
            self.add_col("data", col, "TEXT")

    def add_account(self, name, password):
        # Lowercase the name/username - case must not matter
        name = simple_sqlsafe_str(name.lower())
        cmd = "SELECT * FROM accounts WHERE name = ?"
        qi = queue_item(queue_cmd(cmd, [name]), queue_item.return_type_single)
        account = self.queue_command(qi)
        if account is None:
            # Salt with 24 bytes of random data
            pwsalt = os.urandom(24)
            pwhash = password_hash(password, pwsalt)
            cmd = "INSERT INTO accounts (name, pwhash, pwsalt) VALUES (?,?,?)"
            qi = queue_item(queue_cmd(cmd, [name, pwhash, pwsalt]))
            self.queue_command(qi)
            cmd = "INSERT INTO data (name) VALUES (?)"
            qi = queue_item(queue_cmd(cmd, [name]))
            self.queue_command(qi)

    def get_account(self, name, password):
        # Lowercase the name/username - case must not matter
        name = simple_sqlsafe_str(name.lower())
        cmd = "SELECT * FROM accounts WHERE name = ?"
        qi = queue_item(queue_cmd(cmd, [name]), queue_item.return_type_raw)
        account = self.queue_command(qi)

        if len(account) == 0:
            return None
        if len(account) == 1:
            account = account[0]
            # Main check here if password is correct
            if password_check(account['pwhash'], account['pwsalt'], password):
                return account
            else:
                return False
        if len(account) > 1:
            raise Exception("Multiple accounts with the same name?")

    def start_session(self, name, password):
        # Lowercase the name/username - case must not matter
        name = name.lower()
        account = self.get_account(name, password)
        if account:
            # Create the session and return the uuid
            # the client is responsible for keeping this
            return self.active_sessions.add_session(name)

    def end_session(self, name, session_uuid):
        # Lowercase the name/username - case must not matter
        name = name.lower()
        # End the session, currenly only using the name.
        return self.active_sessions.end_session(name)

    def set_data(self, name, session_uuid, data, value):
        # Lowercase the name/username - case must not matter
        name = name.lower()
        if self.active_sessions.check_session(name, session_uuid):
            # Can't parameterise a column name. Have to do it manually
            cmd = "UPDATE data SET {} = ? WHERE name = ?".format(
                simple_sqlsafe_str(data))
            qi = queue_item(queue_cmd(cmd, [value, name]))
            self.queue_command(qi)
            return True
        else:
            return None

    def get_data(self, name, session_uuid, data):
        # Lowercase the name/username - case must not matter
        name = name.lower()
        # print("get_data: ", name, session_uuid)
        # print(self.active_sessions.session_list)
        if self.active_sessions.check_session(name, session_uuid):
            cmd = "SELECT {} FROM data WHERE name = ?".format(
                simple_sqlsafe_str(data))
            qi = queue_item(queue_cmd(cmd, [name]), queue_item.return_type_single)
            return self.queue_command(qi)
        else:
            return "No active session"


def password_get_digest(password, pw_salt):
    """
    Using sha512 with 15k iterations, appears to be fast enough
    while still being fairly secure, for our use at least

    Using explicit UTF-8 encoding for the string->bytes to make
    sure there are no issues if we have different standard encoding
    """
    return hashlib.pbkdf2_hmac(
        'sha512', 
        password.encode(encoding='UTF-8'), 
        pw_salt, 
        15000
    )

def password_hash(password, pw_salt):
    """
    Hash the provided password with a randomly-generated salt and return the
    salt and hash to store in the database.
    """
    pw_hash = password_get_digest(password, pw_salt)
    return pw_hash


def password_check(pw_hash, pw_salt, password):
    """
    Given a previously-stored salt and hash, and a password provided by a user
    trying to log in, check whether the password is correct.
    """
    return hmac.compare_digest(
        pw_hash,
        password_get_digest(password, pw_salt)
    )


class sessions():

    def __init__(self):
        # print("Session init")
        self.session_list = {}

    def add_session(self, name):
        # Lowercase the name/username - case must not matter
        name = name.lower()
        # If we already have a session for this user, return it
        # allows two devices to log in at the same time
        if name in self.session_list:
            return self.session_list[name][0]
        else:
            # Otherwise make a new uuid, store it against the name
            # in the session dict, with the creation date/time
            new_uuid = uuid.uuid4()
            self.session_list[name] = [new_uuid, datetime.now()]
            # and then return the uuid
            return new_uuid

    def end_session(self, name):
        # Lowercase the name/username - case must not matter
        name = name.lower()
        # print("Removing session for: " + name)
        if self.session_list.pop(name, None):
            return True
        else:
            return False

    def check_session(self, name, session_uuid):
        # Lowercase the name/username - case must not matter
        name = name.lower()
        if name in self.session_list:
            session = self.session_list[name]
            age = (datetime.now() - session[1]).total_seconds()
            if str(session_uuid) != str(session[0]):
                return False
            elif age > (15*24*60*60):
                # Age is 15 days worth of seconds, and if it's
                # old then remove the current session
                self.end_session(name)
                return False
            else:
                return True
        else:
            return False
