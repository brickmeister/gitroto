"""
Managing user tokens credentials

Uses SQLite + S3 to provide credentials
"""

import sqlite3
import boto3
import logging

class GitCredentials:
    def __init__(self,
                 documentdb_table,
                 region_name):
        """
        Initialize the database connection
        """
        
        # set some variables
        self.documentdb_table = documentdb_table

        # set the connection
        self.table = boto3.client("dynamodb", region_name = region_name)

    def get_token(self,
                  user : str) -> str:
        """
        Get the token from the sql databases for a given user
        """
        try:
            _result = self.table.get_item(TableName = self.documentdb_table,
                                          Key={"user": {"S": user}})

            # return the result
            return _result['token']

        except Exception as err:
            logging.warning(f"Failed to get token, error : {err}")
            return "ERROR"

    def set_token(self,
                  user : str,
                  token : str) -> bool:
        """
        Set a token for a user
        """

        try:
            self.table.put_item(TableName = self.documentdb_table,
                                Item={"user": {"S" : user},
                                      "token" : {"S" :  token}})

            return True

        except Exception as err:
            logging.warning(f"Failed to set token, error : {err}")
            return False

    def delete_user(self,
                    user : str) -> bool:
        """
        Delete a user from the table
        """

        try:
            self.table.delete_item(TableName = self.documentdb_table,
                                   Item={"user": {"S" : user}})

            return True
            
        except Exception as err:
            logging.warning(f"Failed to delete user {user}, error : {err}")
            return False

