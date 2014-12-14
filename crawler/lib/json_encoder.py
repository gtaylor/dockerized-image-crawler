"""
Custom JSON encoders.
"""

import json


class JobDataEncoder(json.JSONEncoder):
    """
    Job data uses sets in Redis, so we'll naively encode sets as lists.
    """

    def default(self, obj):
        if isinstance(obj, set):
            return list(obj)
        return super(JobDataEncoder, self).default(obj)
