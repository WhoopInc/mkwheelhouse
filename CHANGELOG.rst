Changelog
=========

All notable changes to this project will be documented in this file.
This project adheres to `Semantic Versioning <http://semver.org/>`_.

`2.0.0`_ - 2016 December 30
-----------------------------

Added
~~~~~

- Unrecognized options will be passed through to ``pip wheel``. This
  means all requested pip options, like ``--no-binary`` and
  ``--cache-dir``, are exposed through mkwheelhouse.

- Canned ACL policies can be specified on the command line, avoiding the
  need for a bucket policy [`#12`_\ ]. Thanks, `@thenoid`_!

Changed
~~~~~~~

- Invoking mkwheelhouse with no requirements (e.g., ``mkwheelhouse
  s3://BUCKET``) generates only a warning instead of an error. This is
  because a bare ``pip wheel`` is not an error, and arguments are now
  passed directly to ``pip wheel``. This behavior may be changed
  upstream; follow `pypa/pip#2720`_ for details.

Fixed
~~~~~

- Bucket URLs generated when IAM roles are in use are now valid [`#11`_\ ].
  Thanks, `@joshma`_!


`1.1.1`_ - 2016 January 23
-----------------------------

Fixed
~~~~~

- mkwheelhouse can actually build wheelhouses in S3 subdirectories
  [`#10`_\ ]. Thanks, `@rajiteh`_!


`1.1.0`_ - 2015 April 24
-----------------------------

Added
~~~~~

- mkwheelhouse learned to build wheelhouses in S3 subdirectories (key
  prefixes) [`#2`_\ ]. Thanks, `@j-martin`_!


`1.0.0`_ - 2015 April 23
------------------------

Changed
~~~~~~~

- Boto replaced Botocore. Boto is a higher-level AWS API that provides
  better error messages. mkwheelhouse's documented functionality should
  remain unchanged, but if you were relying on error messages, you may
  be impacted. **[BREAKING]**
- Documentation converted to reStructuredText.


`0.3.1`_ - 2015 April 23
------------------------

Added
~~~~~

-  This CHANGELOG.
-  Unofficial Python 2.6 support [`#6`_\ ]. Thanks, `@prologic`_!


.. _2.0.0: https://github.com/WhoopInc/mkwheelhouse/compare/1.1.1...2.0.0
.. _1.1.1: https://github.com/WhoopInc/mkwheelhouse/compare/1.1.0...1.1.1
.. _1.1.0: https://github.com/WhoopInc/mkwheelhouse/compare/1.0.0...1.1.0
.. _1.0.0: https://github.com/WhoopInc/mkwheelhouse/compare/0.3.1...1.0.0
.. _0.3.1: https://github.com/WhoopInc/mkwheelhouse/compare/0.3.0...0.3.1

.. _#2: https://github.com/WhoopInc/mkwheelhouse/pull/2
.. _#6: https://github.com/WhoopInc/mkwheelhouse/pull/6
.. _#8: https://github.com/WhoopInc/mkwheelhouse/pull/8
.. _#10: https://github.com/WhoopInc/mkwheelhouse/issues/10
.. _#11: https://github.com/WhoopInc/mkwheelhouse/issues/11
.. _#12: https://github.com/WhoopInc/mkwheelhouse/pull/12

.. _@j-martin: https://github.com/j-martin
.. _@joshma: https://github.com/joshma
.. _@prologic: https://github.com/prologic
.. _@rajiteh: https://github.com/rajiteh
.. _@thenoid: https://github.com/thenoid

.. _pypa/pip#2720: https://github.com/pypa/pip/issues/2720
