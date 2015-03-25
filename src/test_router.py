"""device settings audit"""
import inspect

import pytest

"""
The MIT License (MIT)

Copyright (c) 2015 by Kevin Landreth, David Michael Pennington and
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


@pytest.mark.parametrize("required_line", [
    "maximum-paths 8",
    "redistribute static",
    ])
@pytest.mark.routing_igp
def test_igp_ospf(required_line, device):
    """Verify OSPF router settings
    
    For each ``required_line`` in pytest.mark.parametrize() above, run a 
    seperate pytest to ensure the line is configured under the appropriate IGP.
    """

    IGP_LINE = r"^router\sospf"

    # Find any matching IGP_LINE, in this case 'router ospf'
    igp_objs = device.find_objects(IGP_LINE)
    assert len(igp_objs)==1   # Require exactly one IGP

    igp_obj = igp_objs[0]
    test_val = igp_obj.re_match_iter_typed(required_line, group=0, 
        result_type=str, default="__FAILED__")
    assert test_val!="__FAILED__"

@pytest.mark.parametrize("rejected_line", [
    "redistribute connected",
    ])
@pytest.mark.routing_igp
def test_igp_ospf_negative(rejected_line, device):
    """Verify OSPF router is *not* configured with these lines
    
    For each ``rejected_line`` in pytest.mark.parametrize() above, run a 
    seperate pytest to ensure the line is *not* configured under the 
    appropriate IGP.
    """

    IGP_LINE = r"^router\sospf"
    test_name = inspect.stack()[0][3]+"():"

    # Find any parents matching IGP_LINE, in this case 'router ospf'
    igp_objs = device.find_objects(IGP_LINE)
    assert len(igp_objs)==1   # Require exactly one IGP

    igp_obj = igp_objs[0]
    test_val = igp_obj.re_match_iter_typed(rejected_line, group=0, 
        result_type=str, default="__PASSED__")
    assert test_val=="__PASSED__"

@pytest.mark.ethernet
@pytest.mark.interface
def test_uplinks(device, interface):
    """check uplinks for sanity"""

    test_name = inspect.stack()[0][3]+"():"

    # Find all interfaces with UPLINK in the description
    #   skip all interfaces that *don't* use UPLINK in the description
    uplink_objs = device.find_objects_w_child(
        r'^' + interface + r'\s*$', r'^\s+description\s.*?UPLINK')
    if len(uplink_objs) < 1:
        pytest.skip('{0} not an uplink'.format(test_name))
    elif len(uplink_objs) > 1:
        pytest.fail('{0} more than one uplink matches'.format(test_name))

    uplink = uplink_objs[0]
    uplink_port = uplink.re_match_typed(r'interface\s+\S+.*?(\d+\/\d+.*)\s*$')
    # this could be lag
    if uplink.re_search('[Pp]ort-channel'):
        uplink = device.find_objects('^interface \S+?thernet\s*{0}'
            .format(uplink_port))[0]
    else:
        # FIXME
        pass

    # enabled and with an address
    assert uplink.re_search_children("ipv6 enable")
    assert uplink.re_search_children("ipv6 address ([0-9a-f:]+:[12]/64)")

