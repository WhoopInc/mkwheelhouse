#!/usr/bin/env python

import json
import os
import sys
import traceback

import boto
from boto.s3.connection import Location, OrdinaryCallingFormat

BUCKET_POLICY_PUBLIC = json.dumps({
    'Version': '2008-10-17',
    'Statement': [{
        'Sid': 'AllowPublicRead',
        'Effect': 'Allow',
        'Principal': {'AWS': '*'},
        'Action': ['s3:GetObject'],
        'Resource': ['arn:aws:s3:::%s/*']
    }]
})

if len(sys.argv) != 2 or sys.argv[1] not in ['create', 'delete']:
    sys.exit('usage: {0} [create|delete]'.format(sys.argv[0]))

failed = False

# We have to specify both the desired region and location or API
# requests will fail in subtle ways and undocumented ways: SSL errors,
# missing location constraints, etc.
connections = [
    (os.environ['MKWHEELHOUSE_BUCKET_NONSTANDARD'], 'eu-west-1', Location.EU),
    (os.environ['MKWHEELHOUSE_BUCKET_STANDARD'], 'us-east-1', Location.DEFAULT)
]

for bucket_name, region, location in connections:
    s3 = boto.s3.connect_to_region(region,
                                   calling_format=OrdinaryCallingFormat())
    if sys.argv[1] == 'create':
        bucket = s3.create_bucket(bucket_name, location=location)
        bucket.set_policy(BUCKET_POLICY_PUBLIC % bucket_name)
    else:
        try:
            bucket = s3.get_bucket(bucket_name)
            bucket.delete_keys([key.name for key in bucket.list()])
            bucket.delete()
        except boto.exception.S3ResponseError:
            traceback.print_exc()
            # Don't exit just yet. We may still be able to clean up the
            # other buckets.
            failed = True
            continue

sys.exit(failed)
