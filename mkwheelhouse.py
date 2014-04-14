#!/usr/bin/env python

import argparse
import mimetypes
import subprocess
import tempfile

import botocore.session
import yattag

class Bucket:
    def __init__(self, name):
        self.name = name
        self.s3_service = botocore.session.get_session().get_service('s3')

    def region(self):
        if not hasattr(self, '_region'):
            default_endpoint = self.s3_service.get_endpoint()
            op = self.s3_service.get_operation('GetBucketLocation')
            http_response, response_data = op.call(default_endpoint,
                                                   bucket=self.name)
            self._region = response_data['LocationConstraint']
        return self._region

    def endpoint(self):
        return self.s3_service.get_endpoint(self.region())

    def remote_url(self):
        return 's3://{}'.format(self.name)

    def resource_url(self, resource):
        return '{host}{bucket}/{resource}'.format(
            host=self.endpoint().host,
            bucket=self.name,
            resource=resource)

    def sync(self, local_dir):
        return subprocess.check_call([
            'aws', 's3', 'sync',
            local_dir, self.remote_url(),
            '--region', self.region()])

    def put(self, body, key):
        args = [
            'aws', 's3api', 'put-object',
            '--bucket', self.name,
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
        http_response, response_data = op.call(self.endpoint(), bucket=self.name)

        keys = [obj['Key'] for obj in response_data['Contents']]
        keys = [key for key in keys if key.endswith('.whl')]

        wheels = []
        for key in keys:
            url = self.resource_url(key)
            wheels.append((key, url))

        return wheels

    def index(self):
        doc, tag, text = yattag.Doc().tagtext()
        with tag('html'):
            for name, url in self.wheels():
                with tag('a', href=url):
                    text(name)
                doc.stag('br')

        return doc.getvalue()

def build_wheels(packages, requirements_files):
    packages = packages or []
    requirements_files = requirements_files or []

    temp_dir = tempfile.mkdtemp(prefix='mkwheelhouse-')

    args = ['pip', 'wheel', '--wheel-dir', temp_dir]

    for path in requirements_files:
        args.append('--requirement')
        args.append(path)

    args.extend(packages)

    subprocess.check_call(args)

    return temp_dir

def main():
    parser = argparse.ArgumentParser(description='Generate and upload wheels to an Amazon S3 wheelhouse')
    parser.add_argument('bucket')
    parser.add_argument('-r', '--requirement', metavar='REQUIREMENTS FILE', action='append')
    parser.add_argument('package', nargs='*')

    args = parser.parse_args()

    if not args.requirement and not args.package:
        parser.error('specify at least one requirements file or package')


    bucket = Bucket(args.bucket)

    build_dir = build_wheels(args.package, args.requirement)
    bucket.sync(build_dir)
    bucket.put(bucket.index(), key='index.html')

    print('Index written to:', bucket.resource_url('index.html'))

if __name__ == '__main__':
    main()
