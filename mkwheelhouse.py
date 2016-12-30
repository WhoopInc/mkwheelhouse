#!/usr/bin/env python

from __future__ import print_function
from __future__ import unicode_literals

import argparse
import glob
import json
import mimetypes
import os
import re
import shutil
import subprocess
import sys
import tempfile
from six.moves.urllib.parse import urlparse

import boto
import boto.s3.connection
import yattag


def spawn(args, capture_output=False):
    print('=>', ' '.join(args))
    if capture_output:
        return subprocess.check_output(args)
    return subprocess.check_call(args)


class Bucket(object):
    def __init__(self, url):
        if not re.match(r'^(s3:)?//', url):
            url = '//' + url
        url = urlparse(url)
        self.name = url.netloc
        self.prefix = url.path.lstrip('/')
        # Boto currently can't handle names with dots unless the region
        # is specified explicitly.
        # See: https://github.com/boto/boto/issues/2836
        self.region = self._get_region()
        self.s3 = boto.s3.connect_to_region(
            region_name=self.region,
            calling_format=boto.s3.connection.OrdinaryCallingFormat())
        # Hack to work around Boto bug that generates invalid URLs when
        # query_auth=False and an IAM role is in use.
        # See: https://github.com/boto/boto/issues/2043
        # See: https://github.com/WhoopInc/mkwheelhouse/issues/11
        self.s3.provider.security_token = ''
        self.bucket = self.s3.get_bucket(self.name)

    def _get_region(self):
        # S3, for what appears to be backwards-compatibility
        # reasons, maintains a distinction between location
        # constraints and region endpoints. Newer regions have
        # equivalent regions and location constraints, so we
        # hardcode the non-equivalent regions here with hopefully no
        # automatic support future S3 regions.
        #
        # Note also that someday, Boto should handle this for us
        # instead of the AWS command line tools.
        stdout = spawn([
            'aws', 's3api', 'get-bucket-location',
            '--bucket', self.name], capture_output=True)
        location = json.loads(stdout.decode())['LocationConstraint']
        if not location:
            return 'us-east-1'
        elif location == 'EU':
            return 'eu-west-1'
        else:
            return location

    def get_key(self, key):
        if not isinstance(key, boto.s3.key.Key):
            return boto.s3.key.Key(bucket=self.bucket,
                                   name=os.path.join(self.prefix, key))
        return key

    def has_key(self, key):
        return self.get_key(key).exists()

    def generate_url(self, key):
        key = self.get_key(key)
        return key.generate_url(expires_in=0, query_auth=False)

    def list(self):
        return self.bucket.list(prefix=self.prefix)

    def sync(self, local_dir, acl):
        return spawn([
            'aws', 's3', 'sync',
            local_dir, 's3://{0}/{1}'.format(self.name, self.prefix),
            '--region', self.region, '--acl', acl])

    def put(self, body, key, acl):
        key = self.get_key(key)

        content_type = mimetypes.guess_type(key.name)[0]
        if content_type:
            key.content_type = content_type

        key.set_contents_from_string(body, replace=True, policy=acl)

    def list_wheels(self):
        return [key for key in self.list() if key.name.endswith('.whl')]

    def make_index(self):
        doc, tag, text = yattag.Doc().tagtext()
        with tag('html'):
            for key in self.list_wheels():
                with tag('a', href=self.generate_url(key)):
                    text(key.name)
                doc.stag('br')

        return doc.getvalue()


def build_wheels(index_url, pip_wheel_args, exclusions):
    build_dir = tempfile.mkdtemp(prefix='mkwheelhouse-')
    args = [
        'pip', 'wheel',
        '--wheel-dir', build_dir,
        '--find-links', index_url,
        # pip < 7 doesn't invalidate HTTP cache based on last-modified
        # header, so disable it.
        '--no-cache-dir'
    ] + pip_wheel_args
    spawn(args)
    for exclusion in exclusions:
        matches = glob.glob(os.path.join(build_dir, exclusion))
        for match in matches:
            os.remove(match)
    return build_dir


def parse_args():
    parser = argparse.ArgumentParser(
        description='Generate and upload wheels to an Amazon S3 wheelhouse',
        usage='mkwheelhouse [options] bucket [PACKAGE...] [pip-options]',
        epilog='Consult `pip wheel` for valid pip-options.')
    parser.add_argument('-e', '--exclude', action='append', default=[],
                        metavar='WHEEL_FILENAME',
                        help='wheels to exclude from upload')
    parser.add_argument('-a', '--acl', metavar='POLICY', default='private',
                        help='canned ACL policy to apply to uploaded objects')
    parser.add_argument('bucket',
                        help='the Amazon S3 bucket to upload wheels to')
    args, pip_wheel_args = parser.parse_known_args()
    try:
        run(args, pip_wheel_args)
    except subprocess.CalledProcessError:
        print('mkwheelhouse: detected error in subprocess, aborting!',
              file=sys.stderr)


def run(args, pip_wheel_args):
    bucket = Bucket(args.bucket)
    if not bucket.has_key('index.html'):
        bucket.put('<!DOCTYPE html><html></html>', 'index.html', acl=args.acl)
    index_url = bucket.generate_url('index.html')
    build_dir = build_wheels(index_url, pip_wheel_args, args.exclude)
    bucket.sync(build_dir, acl=args.acl)
    bucket.put(bucket.make_index(), key='index.html', acl=args.acl)
    shutil.rmtree(build_dir)
    print('mkwheelhouse: index written to', index_url)


if __name__ == '__main__':
    parse_args()
