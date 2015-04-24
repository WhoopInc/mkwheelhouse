Testing
=======

No unit testing, since the project is so small. But a full suite of
acceptance tests that run using `Bats: Bash Automated Testing
System <https://github.com/sstephenson/bats>`_!

See `the .travis.yml CI configuration <.travis.yml>`_ for a working
example.

Environment variables
---------------------

You'll need to export the below. Recommended values included when not
sensitive.

.. code:: bash

    # AWS credentials with permissions to create S3 buckets
    export AWS_ACCESS_KEY_ID=
    export AWS_SECRET_ACCESS_KEY=

    # Bucket names, one for the US Standard region and one for
    # a non-US Standard region to test endpoint logic.
    export MKWHEELHOUSE_BUCKET_STANDARD="$USER.mkwheelhouse.com"
    export MKWHEELHOUSE_BUCKET_NONSTANDARD="$USER.eu.mkwheelhouse.com"

Running tests
-------------

You'll need `Bats <https://github.com/sstephenson/bats>`_ installed!
Then:

.. code:: bash

    # export env vars as described
    $ python setup.py develop
    $ test/fixtures.py create
    $ bats test/test.bats
    # hack hack hack
    $ test/fixtures.py delete
