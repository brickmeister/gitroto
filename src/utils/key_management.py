"""
This module genrates a public rsa key
that will be used for deploy keys
"""

from cryptography.hazmat.primitives import serialization as crypto_serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend as crypto_default_backend
import uuid
from collections import namedtuple
from typing import Dict

# named tuple class, used for keys
Keys = namedtuple("Key", "private public title id")

def gen_key() -> namedtuple:
    """
    Generate a rsa key
    """

    # create the ssh key
    key = rsa.generate_private_key(
        backend=crypto_default_backend(),
        # recommended crypto primitive
        public_exponent=65537,
        key_size=4096
    )

    # encode the private key in openssh format
    private_key = key.private_bytes(
        crypto_serialization.Encoding.PEM,
        crypto_serialization.PrivateFormat.PKCS8,
        crypto_serialization.NoEncryption()
    ).decode()

    # encode the public key
    public_key = key.public_key().public_bytes(
        crypto_serialization.Encoding.OpenSSH,
        crypto_serialization.PublicFormat.OpenSSH
    ).decode()

    # create uuid for the key
    _title = str(uuid.uuid4())

    # returning empty string for key_id since it's not set yet
    return Keys(private_key, public_key, _title, "")


class KeyCache:
    """
    This in memory cache maintains a key value store
    of existing keys from this session
    """

    __slots__ = ("_dict")

    def __init__(self):

        # initialize the hash map of namedtuples
        self._dict : Dict[str, Keys] = dict()

    def cache(self, func) -> Keys:
        """
        This is a decorator function
        for caching keys
        """

        def inner_func(*args, **kwargs):
            """
            Check if results can be returned from cache
            Run otherwise and cache
            """

            _repo = kwargs["repo"]

            if _repo in self._dict:
                return self._dict[_repo]
            else:
                _result = func(**kwargs)
                self._dict[_repo]= _result
                
                return self._dict[_repo]

        return inner_func

    def expire(self, func) -> None:
        """
        Remove a key from the cache
        Used as a decorator
        """

        def inner_func(*args, **kwargs):
            """
            Check if key is in cache
            Remove key from cache if it is
            """

            _repo = kwargs["repo"]

            if _repo in self._dict:
                self._dict.pop(_repo)
            _result = func(**kwargs)
                
            return _result

        return inner_func

        
