#!/usr/bin/python
# -*- coding: utf-8 -*-

import json
import sqlite3
from datetime import datetime, timedelta

def main():
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
        try:
            diff_obj = {
                'blocked': [],
                'unblocked': [],
            }

            cursor.execute("SELECT ip FROM block_list WHERE is_blocked=1")
            try:
                with open('last_blocked.json', 'r') as read_file:
                    with open('block_list_with_diff.json', 'w+') as write_file:
                        ip_list = json.loads(read_file.read())
                        for row in cursor.fetchall():
                            ip_new = row[0]
                            if ip_new not in ip_list:
                                diff_obj['unblocked'].append(ip_new)
                            else:
                                diff_obj['blocked'].append(ip_new)
                        write_file.write(json.dumps(diff_obj))
            except IOError:
                print('File last_blocked.json is not exists yet. Please rerun script.')

            cursor.execute("SELECT ip FROM block_list WHERE is_blocked=1")
            with open('last_blocked.json', 'w+') as write_file:
                ip_list = []
                for row in cursor.fetchall():
                    ip_list.append(row[0])
                write_file.write(json.dumps(ip_list))

        except connection.Error:
            print("SQL ERROR!")

    delta = datetime.now() - now
    print('Time delta: {}'.format(delta))

if __name__ == '__main__':
    main()
