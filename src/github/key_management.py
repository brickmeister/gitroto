"""
Managing user tokens credentials

Uses SQLite + S3 to provide credentials
"""

import sqlite3

class GitCredentials:
    def __init__(self,
                 sql_db : str = 'gitroto_db.sqlite'):
        """
        Initialize the database connection
        """

        self.sql_db = sql_db
        self.conn = sqlite3.connect(self.sql_db)
        self.cursor = self.conn.cursor()

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
            print(f"Failed to create user_tokens schema, error : {err}")
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
            print(f"Failed to get token, error : {err}")
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
            print(f"Failed to set token, error : {err}")
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
            print(f"Failed to create user {user}, error : {err}")
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
            print(f"Failed to delete user {user}, error : {err}")
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
            print(f"Failed to close sqlite3 connection, error : {err}")
            return False


    def open_connection(self) -> bool:
        """
        Open a database connect
        """
        
        try:
            self.conn = sqlite3.connect(self.sql_db)
            self.cursor = self.conn.cursor()
            return True

        except Exception as err:
            print(f"Failed to open sqlite3 connection, error = {err}")
            return False


    def load_s3(self) -> bool:
        """
        Read in SQLite database from S3
        """
        pass

    def export_s3(self) -> bool:
        """
        Export SQLite database to S3
        """
        pass