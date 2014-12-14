"""
Contains a really cheezy quasi-FSM for parsing URL bodies.
"""


def parse_linebreakless_url_str(url_str):
    """
    Muddle through a string that contains at least one properly formed URL.
    The example submission method results in the URLs running into one long,
    un-delimited string.

    Rather than require our example user to send linebreaks, we'll just try
    to parse these as best we can.

    :param str url_str: A string containing at least one valid URL.
    :rtype: set
    :returns: A set of URLs found within the string.
    """

    split_body = url_str.split('/')
    urls_to_crawl = set()
    current_urlstr = ''
    is_in_initial_state = True

    for tok in split_body:
        if not tok:
            continue

        if is_in_initial_state and tok not in ['http:', 'https:']:
            raise ValueError("URLs must start with a protocol string.")

        if tok in ['http:', 'https:']:
            if current_urlstr:
                # We already had a URL in the cooker, send it off.
                urls_to_crawl.add(current_urlstr)

            current_urlstr = tok + '//'
            is_in_initial_state = False
        else:
            current_urlstr += tok

    # If we had a URL in the buffer at the end of the loop, send it along.
    if current_urlstr and _is_fully_baked_url(current_urlstr):
        urls_to_crawl.add(current_urlstr)

    return urls_to_crawl


def _is_fully_baked_url(url_str):
    """
    :param str url_str: The URL to spot check.
    :rtype: bool
    :returns: True if ``url_str`` appears to be a fully-formed URL.
    """

    return url_str not in ['http://', 'https://']
