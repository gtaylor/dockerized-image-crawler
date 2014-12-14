"""
This is the main entrypoint for the HTTP web API. This is a simple Twisted
HTTP server that stores job data in Redis, and announces work to be done
to the workers over ZeroMQ.

You can theoretically run multiple instances without them stepping on
one another's feet, since we use UUID4 for job IDs and ZeroMQ for
messaging. We'd just need to adapt the clients to allow them to connect to
multiple PUSH sockets (trivial).

.. note:: If this were a production project, we'd probably want more
    deliverability and durability guarantees than out-of-the-box ZeroMQ
    provides. RabbitMQ, Kafka, etc would probably be better fits.
"""


from twisted.application import service

from crawler.webapi_service.services.web import get_web_service
from crawler.webapi_service.services.zeromq import ZeroMQBroadcastService, \
    ZeroMQRepeaterService

application = service.Application("crawler-webapi")

# Used for announcing crawl jobs to the worker pool.
broadcast_svc = ZeroMQBroadcastService()
broadcast_svc.setServiceParent(application)

# Workers can delegate any sub-links they find to the rest of the worker pool.
repeater_svc = ZeroMQRepeaterService(broadcast_svc)
repeater_svc.setServiceParent(application)

# The HTTP API service.
http_service = get_web_service(broadcast_svc)
http_service.setServiceParent(application)
