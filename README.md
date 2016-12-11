# twitter_web_ui
Web interface for Twitter

### Installation procedure:
0) Install Python3 and PostgreSQL (I've used 9.5) (distribution dependent)

1) Create a PostgreSQL database dedicated for this application:
```bash
# sudo -u postgres createdb $DB_NAME
```
2) Put database name, db user name and db user password
	to twitter_web_ui/settings.py

3) Install virtualenv and run:
```bash
# virtualenv --python=python3 virt_env
# source virt_env/bin/activate
```
4) Install requirements:
```bash
# pip install -r requirements.txt
```
5) Apply migration:
```bash
# ./manage.py migrate
```
6) Run the server with:
```bash
# ./manage.py runserver
```

now you can access an application on http://127.0.0.1:8000/twitter
This is the main page of application
