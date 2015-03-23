import glob
import os

from ciscoconfparse import CiscoConfParse
import configobj
import pytest

"""
The MIT License (MIT)

Copyright (c) 2015 by CrackerJackMack, David Michael Pennington and
contributors.  See AUTHORS for more details.

Some rights reserved.

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

DEVICE_CONFIGS = {}  # Cache CiscoConfParse objects by device name
DEFAULT_CONFIG_FILE = os.path.join(os.path.dirname(
    os.path.realpath(__file__)), 'config.ini')
TESTCONFIG = configobj.ConfigObj(DEFAULT_CONFIG_FILE, raise_errors=True)

def pytest_addoption(parser):
    parser.addoption(
        "--device", action="append", default=[],
        help="device to run tests on. this option can be repeated")


def generate_interface_tests(file_names):
    """generate a tuple of (device_name, interface string) for use
       with pytest_generate_tests"""

    for device_file_name in file_names:

        if not generate_interface_tests:
            continue

        parse = parse_config(device_file_name)
        intf_objs = parse.find_objects(r'^interface')
        for intf in intf_objs:
            # Send (device_name, intf.text) as the name for each test run
            #    see pytest_generate_tests(), below
            yield (device_file_name, intf.text,)

def pytest_generate_tests(metafunc):
    """This is the code which controls how all tests are run:

    Short story:
    - Look in the test function input parameter names... e.g. def test_foo()
      - If `interface` is in the input parameters, run tests *per interface*
      - Otherwise, run tests *per device*
    """

    ## Get the device name from the --device CLI option, or execute against
    ##    all file_names via all_configs() config discovery function
    file_names = metafunc.config.option.device or all_configs()

    ## Lots of magic below... see the pytest docs for a good explanation
    ##    https://pytest.org/latest/parametrize.html#pytest-generate-tests
    ##
    ## metafunc possibilities...
    # - metafunc.addcall
    # - metafunc.cls
    # - metafunc.config
    # - metafunc.fixturenames
    # - metafunc.funcargnames
    # - metafunc.function
    # - metafunc.module
    # - metafunc.parameterize
    if 'interface' in metafunc.fixturenames:
        # this metafunc.parameterize() runs tests per-device, per-interface...
        metafunc.parametrize(
            "device,interface",#Pass device() & interface() fixtures to the test
            generate_interface_tests(file_names), # Name test/iterate with yield
            indirect=True)

    elif 'device' in metafunc.fixturenames:
        # this metafunc.parameterize() runs tests per-device...
        metafunc.parametrize(
            "device",       # Pass device() fixture to the test
            file_names,     # Name test / iterate with the file_names variable
            indirect=True)

def parse_config(device_file_name):
    """Locate the config for ``device_name`` in the ['audits']['config_dir'] 
    directory, then parse the configuration and store in the DEVICE_CONFIGS
    dictionary.
    """

    path = os.path.expanduser(os.path.join(
        TESTCONFIG['audits']['config_dir'], device_file_name))

    if not os.path.exists(path):
        pytest.fail('{0} is not a valid config'.format(path))

    #
    if not DEVICE_CONFIGS.get(path, False):
        DEVICE_CONFIGS[path] = CiscoConfParse(
            config=path, ignore_blank_lines=False, )

    return DEVICE_CONFIGS[path]

@pytest.fixture(scope='session')
def all_configs():
    """Retrieve all configurations from TESTCONFIG['audits']['config_dir']"""

    path = os.path.expanduser(TESTCONFIG['audits']['config_dir'])
    config_names = []
    for glop in ['*conf']:
        config_names.extend(
            os.path.basename(x)
            for x in glob.iglob(os.path.join(path, glop)))
    return config_names

@pytest.fixture(scope='session')
def device(request):
    """initialize and create ciscoconfparase object for the tests"""
    device_name = request.param
    return parse_config(device_name)

@pytest.fixture
def interface(request):
    """Send the interface name to the test"""

    ## request.param returns the string value of the interface thanks to 
    ##    yield values from generate_interface_tests()
    return request.param
