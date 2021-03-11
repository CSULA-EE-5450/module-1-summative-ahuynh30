from typing import Tuple, Dict
import secrets
import nacl.pwhash
import nacl.exceptions
from fastapi import HTTPException, status


class UserDB(object):
    def __init__(self):
        self._accounts: Dict[str, bytes] = {}

    def create_user(self, username: str) -> Tuple[str, str]:
        """
        Creates a user and returns a automatically-generated token (password)
        for the user.  You can generate this token using secrets.token_urlsafe()

        Only the one-way hash is stored in self._accounts.
        Yum.... hash browns!

        To make hashes, read: https://pynacl.readthedocs.io/en/latest/password_hashing/
        In particular, you want to use the nacl.pwhash.str() function.
        NOTE: str expects passwords in bytes!  Use the str type's encode() function
        or the bytes type's decode() function to help you convert.

        :raises: ValueError if the username already exists
        :param username: desired username
        :return: (username, password_token)
        """
        if username not in self._accounts:
            password = secrets.token_urlsafe()  # password.encode('utf-8')
            hash_password = nacl.pwhash.str(bytes(password, 'utf-8'))
            self._accounts[username] = hash_password
            return username, password
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail=f"username {username} is taken.")

    def is_valid(self, username: str, password) -> bool:
        """
        Check whether the given username and password match a user
        present in the UserDB.  The hash of the input password is
        compared to the stored hash.

        See what you can call in nacl.pwhash.verify to verify an input password.

        :param username:
        :param password:
        :return: True if the credentials are valid, False if not.
        """
        if username in self._accounts:
            try:
                return nacl.pwhash.verify(self._accounts[username], password.encode('utf-8'))
            except nacl.exceptions.InvalidkeyError:
                return False
        else:
            return False
