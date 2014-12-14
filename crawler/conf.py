"""
This could be much better done any number of ways. Since we're just cranking
out a quick example, we'll cheeze it up.
"""

import os

REDIS_HOST = os.environ.get('REDIS_HOST', "boot2docker")
REDIS_PORT = os.environ.get('REDIS_PORT', 6379)

ZMQ_PUSHER_HOST = os.environ.get('ZMQ_PUSHER_HOST', 'boot2docker')
ZMQ_PUSHER_PORT = os.environ.get('ZMQ_PUSHER_PORT', 8050)
ZMQ_REPEATER_HOST = os.environ.get('ZMQ_REPEATER_HOST', 'boot2docker')
ZMQ_REPEATER_PORT = os.environ.get('ZMQ_REPEATER_PORT', 8051)

MAX_CRAWL_DEPTH = 1
CRAWLER_USER_AGENT = "gtaylor's dockerized crawler 1.0"
