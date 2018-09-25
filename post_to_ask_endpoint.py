"""Sample script to send a POST to the ask all endpoint."""

import json
import os
import time
import requests
import dotenv

# get secret from env
dotenv.load_dotenv()
data = dict(
    SECRET_PASSWORD=os.getenv('SECRET_PASSWORD')
)

URL = os.getenv('HEROKU_URL')

# hit the health check and sleep while the dyno wakes up
requests.get(URL + '/healthcheck')
time.sleep(10)

# hit the endpoint
res = requests.post(URL + '/ask-all', data=data)
print(json.loads(res.content.decode('utf8')))
