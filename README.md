Overview
========

This project illustrates a proof of concept for how you can use a combination 
of [pytest] and [ciscoconfparse] to build robust tests for your router, switch,
and firewall configurations.

The ``src/`` directory  is where audits are defined.  We use [pytest] to audit 
configurations based on test definitions and the framework defined in:

- ``conftest.py``: Defines how tests are run, and what parameters are passed to tests
- ``test_*.py``: Define individual config tests, which could either run per-router, or per-interface

The configurations for the test are in the ``configs/`` directory

Installation
============

- Copy or clone this repository
- Install [ciscoconfparse], ``pip install --upgrade ciscoconfparse``
- Install [pytest], ``pip install --upgrade pytest==2.4.6``

Running demo tests
==================

- ``cd src/``
- Run one test against all configs: ``py.test --device [config-file-name] [name-of-test]``
- Run one test against one of the configs: ``py.test --device [config-file-name] [name-of-test]``

License and Copyright
=====================

Copyright (c) 2015, Kevin Landreth and David Michael Pennington
Some rights reserved.

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

Licensed permissively with the [MIT license]

[pytest]: https://pytest.org/ "pytest"
[ciscoconfparse]: http://github.com/mpenning/ciscoconfparse/ "ciscoconfparse"
[MIT license]: http://opensource.org/licenses/MIT
