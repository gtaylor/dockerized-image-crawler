"""
Where the sausage is made. This Redis listener passes job announcements off
to :py:func:`crawl_job_url` in this module for crawling.
"""

from twisted.python import log
from twisted.internet.defer import inlineCallbacks, returnValue
from twisted.web.client import readBody

from crawler.lib.data_store import record_images_for_url
from crawler.webapi_service.lib.job_queue import enqueue_crawling_job
from crawler.lib.tx_http import visit_url, get_response_headers
from crawler.conf import MAX_CRAWL_DEPTH
from crawler.crawler_worker.lib.response_parser import parse_response


@inlineCallbacks
def crawl_job_url(delegator_svc, job_id, url, depth):
    """
    Crawl a URL for images. Record any images that we found under the job's
    record in our job store (Redis). If we encounter valid <a href> tags,
    fire off additional crawling announcements for the worker pool to
    tear into together, rather than trying to do it all here.

    :param str job_id: The crawling job's UUID4 string.
    :param str url: The URL to crawl.
    :param int depth: The depth of this crawling job. If it's 0, this is the
        top-level crawl in the job.
    """

    # Abstraction over Twisted's HTTP client. We'll follow redirs, validate
    # SSL certificates, and try to work for most cases.
    response = yield visit_url(url, follow_redirs=True)

    if response.code != 200:
        log.err("URL %s failed with non-200 HTTP code: %d" % (url, response.code))
        returnValue(None)

    headers = get_response_headers(response)
    # If this were a production environment, we'd probably want to try to
    # figure out chunked response body parsing. We could end up with some
    # huge body sizes as-is.
    body = yield readBody(response)
    # Look through the response's body for possible images and other links.
    image_urls, links_to_crawl = parse_response(url, headers, body)
    yield record_images_for_url(job_id, url, image_urls)

    # Rather than try to follow the links in the current invocation, hand
    # these off so the work may be distributed across the pool.
    if links_to_crawl and depth < MAX_CRAWL_DEPTH:
        enqueue_crawling_job(delegator_svc, job_id, links_to_crawl, depth=depth + 1)
