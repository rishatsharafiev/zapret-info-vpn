#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import json
import sqlite3
from datetime import datetime, timedelta

def main():
    try:
        DB_NAME = 'zapret_info.db'

        now =  datetime.now()

        connection = sqlite3.connect(DB_NAME, timeout=30)
        with connection:
            # init cursor
            cursor = connection.cursor()

            # create table if not exist
            create_table_sql = 'create table if not exists block_list (id integer PRIMARY KEY, ip text NOT NULL, created_at TIMESTAMP, updated_at TIMESTAMP, is_blocked INTEGER);'
            cursor.execute(create_table_sql)

            # save diff and last blocked
            cursor.execute("SELECT ip FROM block_list")
            try:
                try:
                    with open('all_blocked.json', 'w+') as write_file:
                        ip_list = [row[0] for row in cursor.fetchall()]
                        write_file.write(json.dumps(ip_list))
                except IOError:
                    print('File all_blocked.json is not exists yet. Please rerun script.')
                    sys.exit(1)

            except connection.Error:
                print("SQL ERROR!")
                sys.exit(1)
    except Exception:
        print("Exception!")
        sys.exit(1)

    delta = datetime.now() - now
    print('Time delta: {}'.format(delta))
    sys.exit(0)

if __name__ == '__main__':
    main()
