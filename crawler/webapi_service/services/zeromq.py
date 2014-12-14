"""
A pair of ZeroMQ services that lets the web service send and relay crawl
announcement messages.
"""

from twisted.python import log
from twisted.application.service import Service
from txzmq import ZmqFactory, ZmqPushConnection, ZmqEndpoint, ZmqPullConnection

from crawler.conf import ZMQ_PUSHER_PORT, ZMQ_REPEATER_PORT


class ZeroMQBroadcastService(Service):
    """
    This is used by the HTTP API to hand crawl jobs off to the crawler pool.
    """

    def __init__(self):
        self.conn = None

    def startService(self):
        factory = ZmqFactory()
        endpoint = ZmqEndpoint('connect', 'tcp://0.0.0.0:%d' % ZMQ_PUSHER_PORT)
        self.conn = ZmqPushConnection(factory, endpoint)

    def send_message(self, message):
        log.msg("Sent crawl announcement: %s" % message)
        self.conn.push(message)


class ZeroMQRepeaterService(Service):
    """
    If a crawler worker finds a sub-link while looking through a page for images,
    it delegates the crawling of that link to the first available worker by
    sending the URL to this repeater. We then turn around and re-broadcast
    the message to the whole pool (through ZeroMQBroadcastService).
    """

    def __init__(self, broadcaster_svc):
        self.conn = None
        self.broadcaster_svc = broadcaster_svc

    def startService(self):
        factory = ZmqFactory()
        endpoint = ZmqEndpoint('connect', 'tcp://0.0.0.0:%d' % ZMQ_REPEATER_PORT)
        self.conn = ZmqPullConnection(factory, endpoint)
        self.conn.onPull = self._message_received

    def _message_received(self, message):
        log.msg("Repeater message received: %s" % message)
        # Turn around and immediately re-broadcast to the entire pool.
        self.broadcaster_svc.send_message(message[0])
