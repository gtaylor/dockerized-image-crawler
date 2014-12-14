"""
Abstracting away Twisted's incredibly verbose HTTP client.
"""

from twisted.internet import reactor
from twisted.internet.defer import inlineCallbacks, returnValue
from twisted.internet.ssl import ClientContextFactory
from twisted.web.client import Agent, RedirectAgent
from twisted.web.http_headers import Headers

from crawler.conf import CRAWLER_USER_AGENT


class WebClientContextFactory(ClientContextFactory):
    """
    This is apparently required for Twisted to do SSL certificate validation
    and store SSL-related state.

    https://twistedmatrix.com/documents/14.0.0/web/howto/client.html#http-over-ssl
    """

    # No idea why this signature differs, but the docs say to do it this way.
    # noinspection PyMethodOverriding
    def getContext(self, hostname, port):
        return ClientContextFactory.getContext(self)


def get_http_agent(follow_redirs):
    """
    :param bool follow_redirs: If True, follow 301/302 redirects transparently.
    :rtype: twisted.web.client.Agent
    :returns: A properly instantiated Agent for Twisted's HTTP client. Optionally
        with redirect-following support.
    """

    contextFactory = WebClientContextFactory()
    agent = Agent(reactor, contextFactory)
    if follow_redirs:
        return RedirectAgent(agent)
    else:
        return agent


@inlineCallbacks
def visit_url(url, follow_redirs):
    """
    This is probably the only function that will be of general interest in
    this module. It abstracts away all of the insanity required to make an
    HTTP request with Twisted's HTTP client.

    :param str url: The URL to visit.
    :param bool follow_redirs: If True, follow 301/302 redirects transparently.
    :returns: A Twisted response which we can read from.
    """

    agent = get_http_agent(follow_redirs)
    response = yield agent.request(
        'GET', url.encode('utf-8'), Headers({'User-Agent': [CRAWLER_USER_AGENT]}))
    returnValue(response)


def get_response_headers(response):
    """
    Pulls the headers from a Twisted response and spits them out in dict form.
    Technically, you probably don't want to do this because of how headers can
    have multiple values. But meh.

    :param response: A Twisted HTTP client response.
    :rtype: dict
    :returns: A dict of header key/vals.
    """

    return {key.lower(): val[0] for key, val in response.headers.getAllRawHeaders()}
