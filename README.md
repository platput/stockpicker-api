# Setup
- activate venv
- install requirements.txt
- create .env file with db url which includes the username and password
- create database
- use alembic to create tables


# EC2 Specific Setup
- Ref https://www.codingforentrepreneurs.com/blog/hello-linux-setup-gunicorn-and-supervisor
- install supervisor - `sudo apt install supervisor`
- `sudo service supervisor start`
- add a config file in `/etc/supervisor/conf.d/`
- `supervisorctl reread`
- `supervisorctl update`
- `sudo supervisorctl status stockpickerapi_gunicorn`

## Supervisor conf
```angular2html
[program:stockpickerapi_gunicorn]
user=ubuntu
directory=/home/ubuntu/stockpickerapi/
command=/home/ubuntu/stockpickerapi/venv/bin/gunicorn --bind 0.0.0.0 -k uvicorn.workers.UvicornWorker main:app
autostart=true
autorestart=true
stderr_logfile=/home/ubuntu/stockpickerapi/gunicorn.err.log
```


