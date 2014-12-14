"""
A pair of ZeroMQ services that let the worker receive crawl jobs and delegate
sub-urls it finds during the process of crawling.
"""

import json

from twisted.python import log
from twisted.application.service import Service
from twisted.internet.defer import inlineCallbacks
from txzmq import ZmqFactory, ZmqPullConnection, ZmqPushConnection, ZmqEndpoint

from crawler.conf import ZMQ_PUSHER_HOST, ZMQ_PUSHER_PORT, ZMQ_REPEATER_HOST, \
    ZMQ_REPEATER_PORT
from crawler.crawler_worker.lib.job_crawler import crawl_job_url


class ZeroMQListenerService(Service):
    """
    This connects to the ZeroMQBroadcastService on the web API service daemon
    and pulls crawling jobs.
    """

    def __init__(self, delegator_svc):
        """

        :param ZeroMQDelegatorService delegator_svc: If, during the process
            of crawling a page, we run into links to other pages, we send
            the link back to the ZeroMQRepeaterService running on the web API
            service, where the first available worker will grab it.
        """

        self.conn = None
        self.delegator_svc = delegator_svc

    def startService(self):
        factory = ZmqFactory()
        bind_point = 'tcp://%s:%d' % (ZMQ_PUSHER_HOST, ZMQ_PUSHER_PORT)
        log.msg("Binding to broadcaster: %s" % bind_point)
        endpoint = ZmqEndpoint('bind', bind_point)
        self.conn = ZmqPullConnection(factory, endpoint)
        self.conn.onPull = self._message_received

    @inlineCallbacks
    def _message_received(self, message):
        """
        We've received a crawl broadcast. Take it and get to work.

        :param str message: A JSON crawler message.
        """

        # Not really sure why this is always a single-member list. Hopefully
        # this doesn't break anything.
        message = message[0]
        log.msg("Message received: %s" % message)
        message_dict = json.loads(message)
        message_dict['depth'] = int(message_dict['depth'])
        # Don't use dict expansion in a prod environment. Breaks with
        # message format changes.
        yield crawl_job_url(self.delegator_svc, **message_dict)


class ZeroMQDelegatorService(Service):
    """
    This is an outbound PUSH connection to the web API ZeroMQRepeaterService
    that allows a worker to delegate any sub-links it finds (instead of taking
    a detour to crawl them on their own).
    """

    def __init__(self):
        self.conn = None

    def startService(self):
        factory = ZmqFactory()
        bind_point = 'tcp://%s:%d' % (ZMQ_REPEATER_HOST, ZMQ_REPEATER_PORT)
        log.msg("Binding to repeater: %s" % bind_point)
        endpoint = ZmqEndpoint('bind', bind_point)
        self.conn = ZmqPushConnection(factory, endpoint)

    def send_message(self, message):
        """
        Matches the signature of ZeroMQBroadcastService so we can use them
        interchangably in the job queue code.

        :param str message: A JSON crawler message.
        """

        log.msg("Delegating job: %s" % message)
        self.conn.push(message)
