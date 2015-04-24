Contributing
============

We love contributions! Pull request away.

Hacking
-------

You'll need Python, of course. Then, check out the code and install the
production and test dependencies:

.. code:: bash

    $ git clone git@github.com:WhoopInc/mkwheelhouse.git
    $ cd mkwheelhouse
    $ pip install -e .
    $ pip install "file://`pwd`#egg=mkwheelhouse[tests]"

Hack away! When you're ready to test, either `run the test
suite <TESTING.rst>`_ or run ``mkwheelhouse`` manually:

.. code:: bash

    $ mkwheelhouse BUCKET PACKAGE

As long as you install mkwheelhouse with ``pip install -e`` or ``setup.py
develop``, the ``mkwheelhouse`` binary will point to your up-to-date
copy in the Git repository.

Guidelines
----------

We do ask that all contributions pass the linter and test suite. Travis
will automatically run these against your contribution once you submit
the pull request, but you can also run them locally as you go!

Linting
~~~~~~~

.. code:: bash

    $ pre-commit run --all-files

You can also install a pre-commit hook to lint all changed files before
every commit:

.. code:: bash

    $ pre-commit install

Testing
~~~~~~~

See `TESTING <TESTING.rst>`_.
