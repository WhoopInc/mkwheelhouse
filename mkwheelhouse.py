#!/usr/bin/env python

from __future__ import print_function

import argparse
import mimetypes
import os
import subprocess
import tempfile

import botocore.session
import yattag


class Bucket:
    def __init__(self, uri):
        self.uri = uri.strip('/')
        split_uri = self.uri.split('/')
        self.name, self.path = split_uri[0], '/'.join(split_uri[1:])
        self.s3_service = botocore.session.get_session().get_service('s3')

    def region(self):
        if not hasattr(self, '_region'):
            default_endpoint = self.s3_service.get_endpoint()
            op = self.s3_service.get_operation('GetBucketLocation')
            http_response, response_data = op.call(default_endpoint,
                                                   bucket=self.uri)
            self._region = response_data['LocationConstraint']
        return self._region

    def endpoint(self):
        return self.s3_service.get_endpoint(self.region())

    def remote_url(self):
        return 's3://{}'.format(self.uri)

    def resource_url(self, resource):
        return os.path.join(self.endpoint().host, self.uri, resource)

    def sync(self, local_dir):
        return subprocess.check_call([
            'aws', 's3', 'sync',
            local_dir, self.remote_url(),
            '--region', self.region()])

    def put(self, body, key):
        args = [
            'aws', 's3api', 'put-object',
            '--bucket', self.uri,
            '--region', self.region(),
            '--key', key
        ]

        content_type = mimetypes.guess_type(key)[0]
        if content_type:
            args += ['--content-type', content_type]

        with tempfile.NamedTemporaryFile() as f:
            f.write(body.encode('utf-8'))
            f.flush()
            args += ['--body', f.name]
            return subprocess.check_call(args)

    def wheels(self):
        op = self.s3_service.get_operation('ListObjects')
        http_response, response_data = op.call(self.endpoint(),
                                               bucket=self.name)
        keys = [obj['Key'] for obj in response_data['Contents']]

        wheels = []
        for key in keys:
            if not key.endswith('.whl'):
                continue
            key_split = key.split('/')
            if not self.path and len(key_split) > 1:
                continue
            elif self.path != '/'.join(key_split[:-1]):
                continue
            file = key_split[-1]
            url = self.resource_url(file)
            wheels.append((file, url))

        return wheels

    def index(self):
        doc, tag, text = yattag.Doc().tagtext()
        with tag('html'):
            for name, url in self.wheels():
                with tag('a', href=url):
                    text(name)
                doc.stag('br')

        return doc.getvalue()


def build_wheels(packages, index_url, download_cache):
    packages = packages or []
    temp_dir = tempfile.mkdtemp(prefix='mkwheelhouse-')
    args = [
        'pip', 'wheel',
        '--wheel-dir', temp_dir,
        '--find-links', index_url
    ]
    if download_cache:
        args += ['--download-cache', download_cache]
    args += packages
    subprocess.check_call(args)
    return temp_dir


def main():
    parser = argparse.ArgumentParser(
        description='Generate and upload wheels to an Amazon S3 wheelhouse')
    parser.add_argument('bucket')
    parser.add_argument('--download-cache')
    parser.add_argument('package', nargs='+')

    args = parser.parse_args()

    bucket = Bucket(args.bucket)
    index_url = bucket.resource_url('index.html')

    build_dir = build_wheels(args.package, index_url, args.download_cache)
    bucket.sync(build_dir)
    bucket.put(bucket.index(), key='index.html')

    print('Index written to:', index_url)


if __name__ == '__main__':
    main()
