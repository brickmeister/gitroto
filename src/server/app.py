"""
Flask App Server for deploy keys
"""

from flask import Flask, jsonify, request
from github import authorization, keys
from typing import Dict

app = Flask(__name__)

@app.route("/")
def hello_world() -> str:
    """
    Simple heartbeat
    """
    return jsonify(hello="world")

@app.route("/get_github_key")
def get_github_key() -> str:
    """
    Retrieve a github key

    Parameters :

    repo     : String : Repo name
    user     : String : Email of user
    password : String : Password/token to authenticate
    owner    : String : Owner of the Repo
    """
    _args : Dict[str, str] = request.args

    _repo = _args['repo']
    _username = _args['user']
    _password = _args['password']
    _owner = _args['owner']

    try:
        _res = keys.get_deploy_key(repo = _repo,
                                   owner = _owner)
        return jsonify(status =  200,
                       result = _res)
    except Exception as e:
        return jsonify(status = 500,
                       result = str(e))

@app.route("/create_github_key")
def create_github_key() -> str:
    """
    Retrieve a github key

    Parameters :

    repo      : String : Repo name
    user      : String : Email of user
    password  : String : Password/token to authenticate
    owner     : String : Owner of the Repo
    read_only : String : Boolean on whether or not repo should be read only
    """
    _args : Dict[str, str] = request.args

    _repo = _args['repo']
    _username = _args['user']
    _password = _args['password']
    _owner = _args['owner']
    _read_only = _args['read_only'].lower() == 'true'

    try:
        _res = keys.create_deploy_key(repo = _repo,
                                      owner = _owner,
                                      read_only = _read_only)
        return jsonify(status =  200,
                       result = _res)
    except Exception as e:
        return jsonify(status = 500,
                       result = str(e))


@app.route("/clone_to_db")
def get_github_key() -> str:
    """
    Clone a repo and submit to Databricks

    Parameters :

    repo     : String : Repo name
    user     : String : Email of user
    password : String : Password/token to authenticate
    owner    : String : Owner of the Repo
    """
    _args : Dict[str, str] = request.args

    _repo = _args['repo']
    _username = _args['user']
    _password = _args['password']
    _owner = _args['owner']

    try:
        _res = keys.get_deploy_key(repo = _repo,
                                   owner = _owner)
        return jsonify(status =  200,
                       result = _res)
    except Exception as e:
        return jsonify(status = 500,
                       result = str(e))


if __name__ == '__main__':
    app.run(host='0.0.0.0')