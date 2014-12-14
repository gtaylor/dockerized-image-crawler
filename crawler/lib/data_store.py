"""
Functions for manipulating and retrieving jobs in the data store. In this
case, it's Redis. If you cared enough to, you could probably turn this stuff
into classes with overridable behavior, but I'm not a big fan of classes for
the sake of classes. This example is on the simple side.

.. note:: While we do use some pipelining, this set of functions have not
    been optimized. There is quite a bit of room for improvement, but probably
    at the sake of readability and simplicity.
"""

import uuid

import txredisapi
from twisted.internet.defer import inlineCallbacks, returnValue

from crawler.conf import REDIS_HOST, REDIS_PORT

# NOTE: We're not multi-threaded currently. If you were to introduce a
# threadpool, this would probably be a bad idea.
__JOB_DATA_REDIS_CONN = None


@inlineCallbacks
def _get_job_data_conn():
    """
    Lazy-load a Redis connection.

    :rtype: ConnectionPool
    :returns: A connection to Redis.
    """

    global __JOB_DATA_REDIS_CONN

    if __JOB_DATA_REDIS_CONN:
        returnValue(__JOB_DATA_REDIS_CONN)

    __JOB_DATA_REDIS_CONN = yield txredisapi.ConnectionPool(
        host=REDIS_HOST, port=REDIS_PORT)
    returnValue(__JOB_DATA_REDIS_CONN)


def _get_job_keys(job_id):
    """
    Each job is comprised of several keys in Redis. Given a job ID, return
    all of the keys that form the job.

    :param str job_id: A job's UUID4 ID string.
    :rtype: dict
    :returns: A dict with the given job's key names in Redis.
    """

    return {
        'all_urls_key': '%s-all_urls_key' % job_id,
        'crawls_pending_key': '%s-crawls_pending' % job_id,
        'crawls_completed_key': '%s-crawls_completed' % job_id,
        'images_key': '%s-images' % job_id,
    }


@inlineCallbacks
def create_job(urls):
    """
    Creates a job in Redis. Since each job is comprised of multiple keys,
    we've got a bit of work to do.

    :param set urls: The URLs to crawl for images.
    :rtype: dict
    :returns: The job data that we stored in Redis. This will quickly be
        out of date, so don't rely on it for much.
    """

    if not urls:
        raise ValueError("No valid URLs provided.")
    job_id = str(uuid.uuid4())
    job_keys = _get_job_keys(job_id)

    conn = yield _get_job_data_conn()
    # Pipeline to get reduce the numer of roundtrips.
    pipeline = yield conn.pipeline()
    pipeline.sadd(job_keys['all_urls_key'], urls)
    pipeline.sadd(job_keys['crawls_pending_key'], urls)
    yield pipeline.execute_pipeline()
    job_data = yield get_job_data(job_id)
    returnValue(job_data)


@inlineCallbacks
def get_job_data(job_id):
    """
    Retrieves the job's various Redis keys, sticks them into a dict, and
    returns it all for easy digestion.

    :param str job_id: A job's UUID4 ID string.
    :rtype: dict
    :return: A dict of job data, aggregated from all of the job's keys.
    """

    conn = yield _get_job_data_conn()

    job_keys = _get_job_keys(job_id)
    # Pipeline to get reduce the numer of roundtrips.
    pipeline = yield conn.pipeline()
    pipeline.smembers(job_keys['all_urls_key'])
    pipeline.smembers(job_keys['crawls_pending_key'])
    pipeline.smembers(job_keys['crawls_completed_key'])
    pipeline.smembers(job_keys['images_key'])
    # We'll end up with one list member per pipelined command, in the
    # order they appear in above.
    rval = yield pipeline.execute_pipeline()
    if not rval[0]:
        # all_urls key should always have at least one entry.
        raise ValueError("Invalid Job ID: %s" % job_id)

    retval = {
        'id': job_id,
        'all_urls': rval[0],
        'crawls_pending': rval[1],
        'crawls_completed': rval[2] or set(),
        'images': rval[3] or set(),
    }
    returnValue(retval)


@inlineCallbacks
def record_images_for_url(job_id, url, images):
    """
    Records images that we've found while crawling.

    :param str job_id: A job's UUID4 ID string.
    :param str url: The URL that the image was found at.
    :param set images: The images found while crawling this URL.
    """
    conn = yield _get_job_data_conn()

    job_keys = _get_job_keys(job_id)
    # Pipeline to get reduce the numer of roundtrips.
    pipeline = yield conn.pipeline()
    pipeline.srem(job_keys['crawls_pending_key'], url)
    pipeline.sadd(job_keys['crawls_completed_key'], url)
    if images:
        pipeline.sadd(job_keys['images_key'], images)
    result = yield pipeline.execute_pipeline()
