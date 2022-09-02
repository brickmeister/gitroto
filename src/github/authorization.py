"""
This module handles Github Authorization to APIs
"""

import json

# open the config file to get the github token
with open("../config/config.json", 'r') as _f:
    _token = json.load(_f)['github_token']

def github_authorize(func):
    """
    Github token decorator
    """

    def inner_func(*args, **kwargs):
        """
        Check if results can be returned from cache
        Run otherwise and cache
        """

        # add token, overwrite if needed
        kwargs['token'] = _token

        # run the function with the authorization token
        return func(**kwargs)

    return inner_func