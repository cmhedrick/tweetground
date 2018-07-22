import os
import sqlite3
from sqlite3 import Error

import config


class DBHelper:

    def __init__(self, db_file=config.DB):
        self.db_file = db_file
        self.db_exists = os.path.isfile(db_file)
        self.conn = sqlite3.connect(db_file, check_same_thread=False)
        self.cur = self.conn.cursor()

    def init_tables(self):
        if not self.db_exists:
            # create profiles
            self.cur.execute(
                """
                CREATE TABLE IF NOT EXISTS PROFILES(
                    ID INTEGER PRIMARY KEY AUTOINCREMENT,
                    TWIT VARCHAR(32),
                    TWIT_ID VARCHAR(32)
                );
                """
            )
            print('[+] PROFILES table created')
            # create tweets
            self.cur.execute(
                """
                CREATE TABLE IF NOT EXISTS TWEETS(
                    ID INTEGER PRIMARY KEY AUTOINCREMENT,
                    TWIT_ID INTEGER,

                    FOREIGN KEY(TWIT_ID) REFERENCES PROFILES(ID)
                );
                """
            )
            print('[+] TWEETS table created')    
            print('[+] DB Created')
            self.db_exists = True
            return True
        else:
            print('[-] Tables not initialized')            
            return False

    def add_profile(self, twit, twit_id):
        """
        add twitter handle to profiles table
        """
        self.cur.execute(
            'INSERT INTO PROFILES(TWIT, TWIT_ID) VALUES (?,?)',
            (twit, twit_id,)
        )
        print('Added to PROFILES Table')
        self.conn.commit()

    def get_twit_db_id(self, twit_id):
        stmt = "SELECT ID FROM PROFILES WHERE TWIT_ID = (?)"
        args = (twit_id, )
        return [x[0] for x in self.cur.execute(stmt, args)]


if __name__ == '__main__':
    dbh = DBHelper()
    dbh.init_tables()
    opt = input('Del db?==> ')
    if 'n' not in opt.lower():
        os.remove(config.DB)
