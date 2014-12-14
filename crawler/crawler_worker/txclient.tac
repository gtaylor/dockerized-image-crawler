"""
This is the main entrypoint for the crawler worker client. We listen on
ZeroMQ for crawler announcements, then do the heavy lifting in hitting the
URLs to crawl.

You'd want to run a bunch of these in your fleet. Probably at least one per
core/processor per machine.

Alternate messaging protocols can be swapped in easily by replacing the
services below.

.. note:: If this were a production project, we'd probably use a proper
    message broker. But we'll keep it simple for the purpose of our example.
"""

from twisted.application import service

from crawler.crawler_worker.services.zeromq import ZeroMQListenerService, \
    ZeroMQDelegatorService

application = service.Application("crawler-worker")

# This is used for handing off any <a href> tags we find during crawling.
# The first idle worker can pick them up instead of each worker recursively
# going as deep as they can.
delegator_svc = ZeroMQDelegatorService()
delegator_svc.setServiceParent(application)

# We listen for crawler job announcements and hand the job off to our crawler
# with this service.
listener_svc = ZeroMQListenerService(delegator_svc)
listener_svc.setServiceParent(application)
