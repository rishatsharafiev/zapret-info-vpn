#!/usr/bin/python
# -*- coding: utf-8 -*-

import sqlite3
import requests
import csv
import re
from contextlib import closing
from datetime import datetime, timedelta

def main():
    DB_NAME = 'zapret_info.db'

    LAST_HOUR = 4
    delta_last_hour = datetime.now() - timedelta(hours = LAST_HOUR)
    ISO_LAST_HOUR = delta_last_hour.strftime('%Y-%m-%dT%H:%M:%SZ')

    GITHUB_OWNER = 'zapret-info'
    GITHUB_REPO = 'z-i'
    GITHUB_API_COMMITS_LIST = 'https://api.github.com/repos/{owner}/{repo}/commits?since={since}'.format(
        owner=GITHUB_OWNER,
        repo=GITHUB_REPO,
        since=ISO_LAST_HOUR,
    )

    response = requests.get(GITHUB_API_COMMITS_LIST, timeout=15)
    response_obj = response.json()

    now =  datetime.now()

    if response_obj:
        last_commit_obj = response_obj[0]
        last_commit_url = last_commit_obj.get('url')

        last_commit_url = 'https://api.github.com/repos/{owner}/{repo}/commits/{sha1}'.format(
            owner=GITHUB_OWNER,
            repo=GITHUB_REPO,
            sha1='c9cb57216644dc4c70d905a02f46c8fd37c18b1b',
        )

        response = requests.get(last_commit_url, timeout=15)
        response_obj = response.json()

        files = [file for file in response_obj.get('files') if file.get('filename', '') == 'dump.csv']

        try:
            file = files[0]
            dump_url = file.get('raw_url', '')
            pattern = re.compile('^((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)(|/[0-9]{1,2})$')

            with closing(requests.get(dump_url, stream=True, timeout=120)) as response:
                ip_list = []
                for line in response.iter_lines():
                    line_list = re.split(';|[|]', line)
                    line_list_strip = map(lambda x: x.strip(), line_list)
                    line_list_filter = filter(lambda x: pattern.search(x), line_list_strip)
                    ip_list.extend(list(line_list_filter))

                ip_list = list(set(ip_list))

                connection = sqlite3.connect(DB_NAME, timeout=30)
                with connection:
                    # init cursor
                    cursor = connection.cursor()

                    # create table if not exist
                    create_table_sql = 'create table if not exists block_list (id integer PRIMARY KEY, ip text NOT NULL, created_at TIMESTAMP, updated_at TIMESTAMP, is_blocked INTEGER);'
                    cursor.execute(create_table_sql)

                    try:
                        # update all as non blocked
                        cursor.execute("UPDATE block_list SET is_blocked=0")
                        connection.commit()

                        # iterate over ip list and apply insert/update actions
                        counter = 1
                        for ip_item in ip_list:
                            cursor.execute("UPDATE block_list SET updated_at=datetime('now','localtime'), is_blocked=1 WHERE ip=?", (ip_item, ))
                            updated_count = cursor.rowcount
                            if not updated_count:
                                cursor.execute("INSERT INTO block_list (ip, created_at, updated_at, is_blocked) VALUES (?, datetime('now','localtime'), datetime('now','localtime'), 1)", (ip_item, ))
                                inserted_count = cursor.rowcount
                            if updated_count:
                                print('Updated: {}'.format(ip_item))
                            elif inserted_count:
                                print('Inserted: {}'.format(ip_item))
                            else:
                                print('Failed: {}'.format(ip_item))
                            counter += 1
                            if counter % 1000 == 0:
                                print('--> Batch iteration: {}'.format(counter))
                                connection.commit()

                    except connection.Error:
                        print("SQL ERROR!")
        except IndexError:
            print("IndexError")

        delta = datetime.now() - now
        print('Total count: {}, Time delta: {}'.format(len(ip_list), delta))

if __name__ == '__main__':
    main()
