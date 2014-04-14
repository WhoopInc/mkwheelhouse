# mkwheelhouse

Amazon S3 wheelhouse generator.

Wheels are the latest standard in distributing binary for Python. Wheels cut
down scipy's installation time from 15 minutes to 15 seconds.

> [Wheel documentation][wheel-docs]

## Usage

Generate wheels for all packages in `requirements_file` or listed
`package`s and upload them to Amazon S3 `bucket`:

```bash
$ mkwheelhouse <bucket> [-r <requirements file>...] [<package>...]
```

Then install with Pip like usual, but preferring generated wheels:

```bash
$ pip install --find-links <bucket>/index.html -r requirements.txt
```

### Tips

Specify `--find-links` in your requirements file to skip generating wheels that
already exist.

```
# requirements.txt

-f https://s3-us-west-2.amazonaws.com/wheelhouse.whoop.com/index.html

scipy
```

## Notes

* Python 3 only.

* Set a [bucket policy to make all objects publicly accessible][public-policy]
  or Pip won't  be able to download wheels from your wheelhouse.

[public-policy]: http://docs.aws.amazon.com/AmazonS3/latest/dev/AccessPolicyLanguage_UseCases_s3_a.html
[wheel-docs]: http://wheel.readthedocs.org/en/latest/
