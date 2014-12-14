"""
Assorted utility functions that are generally useful, but don't fit in
nicely in any one place.
"""

import re

CR_LF_REGEX = re.compile("[\n\t\r]")


def remove_cr_and_lf(str_to_chomp):
    """
    rstrip() isn't going to remove every funky combination of \n and \r, so
    we'll just do a regex substitution so we don't have to worry about it.

    :param str str_to_chomp: The string that needs chomping.
    :rtype: str
    :returns: The chomped string.
    """

    return CR_LF_REGEX.sub("", str_to_chomp)
