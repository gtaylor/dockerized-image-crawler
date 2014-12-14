"""
A quick and dirty HTTP response parser. Picks out interesting bits of data
and tosses it out for other pieces higher on the stack to use.
"""

from urlparse import urljoin

from bs4 import BeautifulSoup
from twisted.python import log


def parse_response(response_url, headers, body):
    """
    Look through a Twisted HTTP response for images to record and links
    to follow.

    :param str response_url: The URL that the response came from.
    :param dict headers: A dict of response headers.
    :param str body: The full response body.
    :rtype: tuple
    :returns: A tuple of sets in the form of (image_response_url_set,
        links_to_crawl_set).
    """

    # TODO: Might consider making these exceptions.
    if 'content-type' not in headers:
        log.err('Missing Content-Type header. Skipping.')
        return set(), set()
    content_type = headers['content-type'].lower()
    if 'text/html' not in content_type:
        log.err('Content type "%s" not parseable. Skipping.' % content_type)
        return set(), set()

    # If this were a production environment, we'd probably want to try to
    # figure out chunked response body parsing. We could end up with some
    # huge body sizes as-is.
    soup = BeautifulSoup(body)
    image_response_url_set = set([])
    links_to_crawl_set = set([])

    for tag in soup.find_all(['a', 'img']):
        if tag.name == 'a':
            _record_link(response_url, tag, links_to_crawl_set)
        elif tag.name == 'img':
            _record_image(response_url, tag, image_response_url_set)

    return image_response_url_set, links_to_crawl_set


def _record_image(response_url, tag, image_response_url_set):
    img_src = tag.get('src')
    if not img_src:
        return
    image_response_url = _guess_absolute_response_url(response_url, img_src)
    image_response_url_set.add(image_response_url)


def _record_link(response_url, tag, links_to_crawl_set):
    link_href = tag.get('href')
    if not link_href:
        return
    link_response_url = _guess_absolute_response_url(response_url, link_href)
    links_to_crawl_set.add(link_response_url)


def _guess_absolute_response_url(response_url, relative_or_absolute_response_url):
    """
    Given an absolute or relative URL, try to guess the absolute URL in
    the case that the latter is passed in.

    :param str response_url: The URL that generated this response.
    :param str relative_or_absolute_response_url: Either an absolute URL,
        or a relative URL that we will try to make absolute.
    :rtype: str
    :returns: A hopefully valid absolute URL.
    """

    if relative_or_absolute_response_url.startswith('/'):
        # Definitely relative. This usually gives us something usable.
        return urljoin(response_url, relative_or_absolute_response_url)
    elif relative_or_absolute_response_url.startswith('https://') or \
            relative_or_absolute_response_url.startswith('http://'):
        # Looks to already be absolute.
        return relative_or_absolute_response_url
    else:
        # This is either a relative without a leading slash, or it's junk.
        # TODO: Make this behavior configurable.
        return urljoin(response_url, relative_or_absolute_response_url)
