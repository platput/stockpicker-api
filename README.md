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
```supervisor
[program:stockpickerapi_gunicorn]
user=ubuntu
directory=/home/ubuntu/stockpickerapi/
command=/home/ubuntu/stockpickerapi/venv/bin/gunicorn --bind 0.0.0.0 -k uvicorn.workers.UvicornWorker main:app --timeout 300
autostart=true
autorestart=true
stderr_logfile=/home/ubuntu/stockpickerapi/gunicorn.err.log
```

## DB commands for dev env
- `sudo -u postgres pg_dump -c stockpicker > 19feb2022.sql`
- `scp -i privatekey.pem user@domain.com:./filename.ext filename.ext
  19feb2022.sql`
- `psql dbname -U dbuser < dbfile.sql`


## Cron/Lambda setup
```python
import json
from datetime import datetime
import dateutil.tz
import requests

def lambda_handler(event, context):
    holidays = ["01/01/2022", "01/02/2022", "01/08/2022", "01/09/2022", "01/15/2022", "01/16/2022", "01/22/2022", "01/23/2022", "01/29/2022", "01/30/2022", "02/05/2022", "02/06/2022", "02/12/2022", "02/13/2022", "02/19/2022", "02/20/2022", "02/26/2022", "02/27/2022", "03/01/2022", "03/05/2022", "03/06/2022", "03/12/2022", "03/13/2022", "03/18/2022", "03/19/2022", "03/20/2022", "03/26/2022", "03/27/2022", "04/02/2022", "04/03/2022", "04/09/2022", "04/10/2022", "04/14/2022", "04/15/2022", "04/16/2022", "04/17/2022", "04/23/2022", "04/24/2022", "04/30/2022", "05/01/2022", "05/03/2022", "05/07/2022", "05/08/2022", "05/14/2022", "05/15/2022", "05/21/2022", "05/22/2022", "05/28/2022", "05/29/2022", "06/04/2022", "06/05/2022", "06/11/2022", "06/12/2022", "06/18/2022", "06/19/2022", "06/25/2022", "06/26/2022", "07/02/2022", "07/03/2022", "07/09/2022", "07/10/2022", "07/16/2022", "07/17/2022", "07/23/2022", "07/24/2022", "07/30/2022", "07/31/2022", "08/06/2022", "08/07/2022", "08/09/2022", "08/13/2022", "08/14/2022", "08/15/2022", "08/20/2022", "08/21/2022", "08/27/2022", "08/28/2022", "08/31/2022", "09/03/2022", "09/04/2022", "09/10/2022", "09/11/2022", "09/17/2022", "09/18/2022", "09/24/2022", "09/25/2022", "10/01/2022", "10/02/2022", "10/05/2022", "10/08/2022", "10/09/2022", "10/15/2022", "10/16/2022", "10/22/2022", "10/23/2022", "10/24/2022", "10/26/2022", "10/29/2022", "10/30/2022", "11/05/2022", "11/06/2022", "11/08/2022", "11/12/2022", "11/13/2022", "11/19/2022", "11/20/2022", "11/26/2022", "11/27/2022", "12/03/2022", "12/04/2022", "12/10/2022", "12/11/2022", "12/17/2022", "12/18/2022", "12/24/2022", "12/25/2022", "12/31/2022"]
    indian_timezone = dateutil.tz.gettz('Asia/Kolkata')
    current_indian_date = datetime.now(tz=indian_timezone).strftime("%m/%d/%Y")
    if current_indian_date not in holidays:
        req = requests.get('https://stockapi.techtuft.com/scrape/mc')
        scrape_response = req.json()
        if scrape_response.get("success") == True:
            req = requests.get('https://stockapi.techtuft.com/shortlist/create')
            short_list_response = req.json()
            if short_list_response.get("success") == True:
                response = {
                    'success': True,
                    'message': f'{scrape_response.get("message")}, {short_list_response.get("message")}'
                }
                return {
                    'statusCode': 200,
                    'body': response
                }
            else:
                response = {"success": False, "message": f'Data fetched. {short_list_response.get("message")}'}
                return {
                    'statusCode': 201,
                    'body': response
                }
        
        return {
            'statusCode': 201,
            'body': {"success": False, "message": f'Data not fetched.'}
        }
    else:
        try:
            # Update the missing stock symbols on holidays
            req = requests.get('https://stockapi.techtuft.com/scrape/update-symbols')
            scrape_response = req.json()
            if scrape_response.get("success") == True:
              response = {
                'statusCode': 200,
                'body': {
                  'success': True,
                  'message': f'Updated the missing stock symbols, did not scrape the data as stockmarket is closed for the day.'
                }
              }
            else:
              response = {
                'statusCode': 201,
                'body': {
                  'success': False,
                  'message': f'Failed to updated the missing stock symbols. Did not scrape the data as stockmarket is closed for the day.'
                }
              }
        except Exception as e:
            response = {
              'statusCode': 201,
              'body': {"success": False, "message": f"Failed to updated the missing stock symbols. Did not scrape the data as stockmarket is closed for the day. Error: {e}"}
            }
        return response
```
## Redis setup
Redis is needed to store the sectorial-indices data which will be kept in the redis store for 1 hour for now. The data will be reloaded if ite being accessed after one hour.
This is done to avoid the data being stale.

Redis is setup using the official docker image and here is the command to set it up. This docker doesn't have password protection, so aws ec2 instance must not open the port **6379**.
Once everything is dockerized, the redis container should not expose the port and the -p from the command can be removed.

`sudo docker run -p6379:6379  --name stockcache -d redis`


