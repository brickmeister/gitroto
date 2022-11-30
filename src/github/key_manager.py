"""
Managing user tokens credentials

Uses SQLite + S3 to provide credentials
"""

import sqlite3
import boto3
import logging

class GitCredentials:
    def __init__(self,
                 s3_bucket : str = None,
                 sqlite_file : str = 'gitroto.sqlite3'):
        """
        Initialize the database connection
        """
        
        # set some variables
        self.s3_bucket = s3_bucket
        self.sqlite_file = sqlite_file

        # load file from s3
        if self.s3_bucket == 'None':
            self.s3_bucket = s3_bucket
            self.boto_client = boto3.client('s3')
            self.load_s3()

        # open a connection
        self.open_connection()

    def load_db_from_s3(self) -> bool:
        """
        load a sqlite3 database from s3
        """

        try:
            # close existing sqlite3 connection
            self.conn.close()

            # download database from s3
            self.load_s3()

            # load the new connection
            self.conn = sqlite3.connect(self.sqlite_file)
            self.cursor = self.conn.cursor()

            return True
        
        except Exception as err:
            logging.warning(f"Failed to load database from S3, error = {err}")
            return False

    def create_schema(self) -> bool:
        """
        Create the schema associated with the database
        """

        try:
            _result = self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_tokens (
                    user TEXT PRIMARY KEY,
                    token TEXT
                    );
            """)

            self.conn.commit()

            return True

        except Exception as err:
            logging.warning(f"Failed to create user_tokens schema, error : {err}")
            return False


    def get_token(self,
                  user : str) -> str:
        """
        Get the token from the sql databases for a given user
        """
        try:
            _result = self.cursor.execute("""
                SELECT
                    user,
                    token
                FROM
                    user_tokens
                WHERE
                    user = ?;
            """, (user,))

            self.conn.commit()

            # return the result
            return _result.fetchone()[1]

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
            _result = self.cursor.execute("""
                UPDATE user_tokens
                    SET token = ?
                WHERE user = ?;
            """, (token, user)
            )

            self.conn.commit()

            return True

        except Exception as err:
            logging.warning(f"Failed to set token, error : {err}")
            return False


    def create_user(self,
                    user : str) -> bool:
        """
        Create a user if the user doesn't exist
        """

        try:
            _result = self.cursor.execute("""
                INSERT INTO user_tokens(user, token)
                    VALUES (?, ?);
            """, (user, None))

            return True

            self.conn.commit()

        except Exception as err:
            logging.warning(f"Failed to create user {user}, error : {err}")
            return False

    def delete_user(self,
                    user : str) -> bool:
        """
        Delete a user from the table
        """

        try:
            _result = self.cursor.execute("""
                DELETE FROM user_tokens
                    WHERE user = ?;)
            """, (user,))

            self.conn.commit()

            return True
            
        except Exception as err:
            logging.warning(f"Failed to delete user {user}, error : {err}")
            return False

        # return the result
        # TODO ADD CHECK
        return True

    def close_connection(self) -> bool:
        """
        Close the sqlite3 connection
        """

        try:
            self.cursor.close()
            return True

        except Exception as err:
            logging.warning(f"Failed to close sqlite3 connection, error : {err}")
            return False


    def open_connection(self) -> bool:
        """
        Open a database connect
        """
        
        try:
            self.conn = sqlite3.connect(self.sqlite_file)
            self.cursor = self.conn.cursor()
            return True

        except Exception as err:
            logging.warning(f"Failed to open sqlite3 connection, error = {err}")
            return False

    def load_s3(self) -> bool:
        """
        Read in SQLite database from S3
        """
        
        try:
            # download sql lite database to current directory
            self.boto_client.download_file(self.s3_bucket, self.sqlite_file, self.sqlite_file)
            return True

        except Exception as err:
            logging.warning(f"Failed to download sqlite database from S3, error : {err}")
            return False

    def export_s3(self) -> bool:
        """
        Export SQLite database to S3
        """
        
        try:
            # upload sql lite database to s3 bucket
            self.boto_client.upload_file(self.s3_bucket, self.sqlite_file, self.sqlite_file)
            return True

        except Exception as err:
            logging.warning(f"Failed to upload sqlite database from S3, error: {err}")
            return False