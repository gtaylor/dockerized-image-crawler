"""
A simple crawl queue management module. This is currently powered by ZeroMQ
for the sake of simplicity. If we were more concerned about durability,
RabbitMQ, Kafka, or any number of alternatives are a better fit.
"""

import json


def enqueue_crawling_job(delegate_or_broadcast_svc, job_id, urls, depth):
    """
    Used to enqueue a crawling job (or delegate a sub-url on a current job)
    to the worker pool.

    :type delegate_or_broadcast_svc: ZeroMQDelegatorService or
        ZeroMQBroadcastService.
    :param delegate_or_broadcast_svc: The web API service uses a
        ZeroMQBroadcastService to announce new crawling jobs. The crawler
        service uses ZeroMQDelegatorService to delegate any sub-links found
        while scouring a page.
    :param int job_id: The job ID that these URLs fall under.
    :param set urls: The URLs to crawl. We'll send out one announcement
        per URL.
    :param int depth: The depth that this crawl will be at. 0 being initial.
    :rtype: int
    :returns: The number of crawler announcements made. One per URL.
    """

    message_dict = {
        'job_id': job_id,
        'depth': depth
    }
    for url in urls:
        message_dict['url'] = url
        message_str = json.dumps(message_dict)
        delegate_or_broadcast_svc.send_message(message_str)
    return len(urls)
