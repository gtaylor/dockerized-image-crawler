"""
This could be much better done any number of ways. Since we're just cranking
out a quick example, we'll cheeze it up.

Fig no longer recommends env vars, but I noticed this pretty late on and
don't have time to adjust.
"""

import os

REDIS_HOST = os.environ.get('REDIS_1_PORT_6379_TCP_ADDR', '127.0.0.1')
REDIS_PORT = int(os.environ.get('REDIS_1_PORT_6379_TCP_PORT', 6379))

ZMQ_PUSHER = os.environ.get('WEB_1_PORT_8050_TCP', 'tcp://127.0.0.1:8050')

ZMQ_REPEATER = os.environ.get('WEB_1_PORT_8051_TCP', 'tcp://127.0.0.1:8051')

MAX_CRAWL_DEPTH = 1
CRAWLER_USER_AGENT = "gtaylor's dockerized crawler 1.0"
