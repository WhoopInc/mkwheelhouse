mkwheelhouse
============

.. image:: https://travis-ci.org/WhoopInc/mkwheelhouse.svg?branch=master
    :target: https://travis-ci.org/WhoopInc/mkwheelhouse
    :align: right

Amazon S3 wheelhouse generator.

Wheels are the latest standard in distributing binary for Python. Wheels
cut down scipy's installation time from 15 minutes to 15 seconds. `Learn more
about wheels. <http://wheel.readthedocs.org/en/latest/>`_

Usage
-----

Generate wheels for all listed ``PACKAGE``\ s and their dependencies,
then upload them to Amazon S3 ``BUCKET``:

.. code:: bash

    $ mkwheelhouse [options] BUCKET [PACKAGE...] [pip-options]

Then install with pip like usual, but preferring generated wheels:

.. code:: bash

    $ pip install --find-links BUCKET/index.html PACKAGE

You can also build a wheelhouse in an `S3 subdirectory`_ by specifying
the full S3 path:

.. code:: bash

    $ mkwheelhouse s3://BUCKET/SUB/DIRECTORY PACKAGE

.. _S3 subdirectory: http://docs.aws.amazon.com/AmazonS3/latest/UG/FolderOperations.html

Additional options
~~~~~~~~~~~~~~~~~~

- ``-h``, ``--help``

  Print usage information and exit.

- ``-e``, ``--exclude WHEEL_FILENAME``

  Don't upload built wheel with filename WHEEL\_FILENAME. Note this is the
  final wheel filename, like ``argparse-1.3.0-py2.py3-none-any.whl``,
  *not* the bare package name.

  Specifying an exclusion will not remove pre-existing built wheels from
  S3; you'll have to remove those wheels from the bucket manually.

- ``-a``, ``--acl POLICY``

  Apply canned ACL policy POLICY to the uploaded wheels and index.
  Specifying ``public-read``, for example, will make the uploaded wheels
  and index publicly accessible, avoiding the need for for a bucket
  policy to do the same. Valid values for POLICY can be found in the
  `AWS documentation`_.

.. _AWS documentation: http://docs.aws.amazon.com/AmazonS3/latest/dev/acl-overview.html#canned-acl

Any unrecognized options are passed directly to ``pip wheel``. That
means mkwheelhouse supports requirements files, for example:

.. code:: bash

    $ mkwheelhouse s3://BUCKET -r requirements.txt

Need an install log? Need to compile from source? You got it.

.. code:: bash

    $ mkwheelhouse s3://BUCKET --log log.txt --no-binary :all: numpy

Consult ``pip wheel`` for a complete list of pip-options.

Notes
-----

- Python 2 and 3

- Set a `bucket policy to make all objects publicly accessible
  <http://docs.aws.amazon.com/AmazonS3/latest/dev/AccessPolicyLanguage_UseCases_s3_a.html>`_
  or Pip won't be able to download wheels from your wheelhouse.
