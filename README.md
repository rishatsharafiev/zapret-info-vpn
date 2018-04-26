# IP List for VPN

### import source 
https://github.com/zapret-info/z-i

### Install sqlite3
```
sudo apt-get install sqlite3 libsqlite3-dev
```

### install pipenv

```
$ pip install pipenv
```

if you're using Ubuntu 17.10:
```
$ sudo apt install software-properties-common python-software-properties
$ sudo add-apt-repository ppa:pypa/ppa
$ sudo apt update
$ sudo apt install pipenv
```

### create virtualenv
```
pipenv shell --python 2.7
```

### use virtualenv
pipenv shell

### pipenv not available
you can install packages from Pipfile section [packages] manually

### install requirements
```
pipenv install
```

### crontab with pipenv
```
crontab -e
```

```
0 */3 * * * /var/www/django/.local/share/virtualenvs/project-h6ndvli3/bin/python import_csv_to_db.py && /var/www/django/.local/share/virtualenvs/project-h6ndvli3/bin/python export_blocked_list.py 
```
