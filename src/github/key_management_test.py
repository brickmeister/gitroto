"""
Test script to test user_token key management
"""

from key_management import GitCredentials

# initialize the db
_git_db = GitCredentials("gitroto_db")

try:
    # assert creation of schema
    assert(_git_db.create_schema() == True)

    # create a user
    assert(_git_db.create_user("mark") == True)

    # set a token for the user
    assert(_git_db.set_token("mark", "sdfasdfasdfdas") == True)

    # confirm the token was properly set
    assert(_git_db.get_token("mark") == "sdfasdfasdfdas")

    # close the database connection
    assert(_git_db.close_connection() == True)

    # reopen the database connection
    assert(_git_db.open_connection() == True)

    # check to see if tokens were persisted
    assert(_git_db.get_token("mark") == "sdfasdfasdfdas")

    # print a statement
    print("All checks passed")

except Exception as err:
    print(f"Failed check with following error : {err}")