"""
This module provides functions
which interacts with the Github
Deploy Keys API

Docs : https://docs.github.com/en/rest/deploy-keys
"""

import requests
import json
from typing import Dict, List
from utils.key_management import gen_key, KeyCache, Keys
from authorization import github_authorize

_github_url : str = "https://api.github.com/repos"

# TODO : remove this when we have the main class
_key_cache = KeyCache()

@_key_cache.cache
@github_authorize
def create_deploy_key(repo: str, 
                      owner: str,
                      token : str,
                      read_only : bool = True) -> List[Keys]:

    # generate a new key pair
    _key = gen_key()

    # modify the url to add key
    _url : str = '/'.join([_github_url, owner, repo, "keys"])

    # key title
    _title : str = '_'.join([owner, repo, _key.title])

    # create the post dictionary
    _post : Dict[str, str] = {"read_only" : read_only,
                              "key" : _key.public,
                              "title" : _title}

    response : Dict = requests.post(_url, 
                                    data = json.dumps(_post),
                                    headers = {"Accept" : "application/vnd.github+json",
                                               "Authorization" : f"token {token}"}
                                               ).json()

    return [Keys(_key.private, _key.public, _key.title, response["id"])]

@_key_cache.cache
@github_authorize
def get_deploy_key(repo: str, 
                   owner: str,
                   token : str) -> List[Keys]:
    """
    Retrieve a list of deploy keys for repo
    """

    # modify the url to add key
    _url : str = '/'.join([_github_url, owner, repo, "keys"])

    # add in authorization header
    _header = {"Accept" : "application/vnd.github+json",
               "Authorization" : f"token {token}"}

    response : Dict = requests.get(_url,
                                   headers = _header
                                               ).json()

    if len(response) > 0:
       return [Keys('', _res['key'], _res['title'], str(_res['id'])) for _res in response]
    else:
        raise ValueError("Key not found")

@_key_cache.expire
@github_authorize
def expire_deploy_key(repo: str, 
                      owner: str,
                      token : str,
                      key_id : str) -> str:
    """
    Delete a deploy key
    """

    # modify the url to add key
    _url : str = '/'.join([_github_url, owner, repo, "keys", key_id])

    # add in authorization header
    _header = {"Accept" : "application/vnd.github+json",
               "Authorization" : f"token {token}"}

    response : Dict = requests.delete(_url,
                                      headers = _header
                                      )

    return response.status_code
