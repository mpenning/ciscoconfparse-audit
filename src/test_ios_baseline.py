import re

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

###
### Required config lines
###
@pytest.mark.parametrize("required_line", [
    r'service timestamps debug datetime msec localtime show-timezone',
    r'service timestamps log datetime msec localtime show-timezone',
    r'clock timezone MST -7',
    r'service tcp-keepalives-in',
    r'service tcp-keepalives-out',
    r'ip tcp selective-ack',
    r'ip tcp timestamp',
    r'ip tcp synwait-time 10',
    r'ip tcp path-mtu-discovery',
    r'memory reserve critical 4096',])
def test_basics_exact(device, required_line):
    """Required global configurations"""
    assert bool(device.find_lines(r'^'+required_line, exactmatch=True))

###
### Required partial config lines
###
@pytest.mark.parametrize("required_line", [
    r'clock summer-time MDT recurring',
    r'enable secret',
    r'hostname',])
def test_basics_partial(device, required_line):
    """Required global configurations"""
    assert bool(device.find_lines(r'^'+required_line, exactmatch=False))


###
### SNMP checks
###
@pytest.mark.parametrize("required_line", [
    r'snmp-server community {0} [rR][oO] 99'.format(re.escape('g1v3mE$t@t$')),
    r'snmp-server community {0} [rR][wW] 99'.format(re.escape('SoMeThaNGwIErd')),
    ])
def test_snmp(device, required_line):
    """Required global configurations"""
    assert bool(device.find_lines(required_line, exactmatch=True))

@pytest.mark.parametrize("rejected_line", [
    r'snmp-server\scommunity\s\S+\s+[rR][wW]',
    r'snmp-server\scommunity\s\S+\s+[rR][oO]',
    ])
def test_snmp_acl_required(device, rejected_line):
    """Reject all SNMP communities with no ACLs"""
    assert not bool(device.find_lines(rejected_line, exactmatch=True))


###
### Required logging configurations
###
@pytest.mark.parametrize("required_line", [
    r'logging 172.16.15.2',
    r'logging buffered 65535 debugging', ])
def test_logging(device, required_line):
    """Required logging configs"""
    assert bool(device.find_lines(r'^'+required_line, exactmatch=True))

###
### Disable these services
###
@pytest.mark.parametrize("required_line", [
    r'no service pad',
    r'no ip domain-lookup',
    r'ip ospf name-lookup',
    r'no ip source-route',
    r'no ip gratuitous-arps',  # WARNING: HA clustering may require Grat ARP
    ])
def test_services_disabled(device, required_line):
    """disable services"""
    assert bool(device.find_lines(r'^' + required_line, exactmatch=True))

###
### Reject these services
###
@pytest.mark.parametrize("rejected_line", [
    r'service internal',  # You should know what you're doing if you turn it on
    r'enable password',   # Reject insecure enable passwords
    r'ip http server',
    r'ip http secure-server', 
    r'ntp master',
    ])
def test_services_rejected(device, rejected_line):
    """reject services"""
    assert not bool(device.find_lines(r'^' + rejected_line, exactmatch=True))

@pytest.mark.parametrize("required_line", [
    r' logging synchronous',
    r' exec-timeout 5 0',
    r' transport preferred none',
    ])
def test_vty(device, required_line):
    """Required vty configs"""
    VTY_REGEX = r'line\svty\s(\d.+)\s*$'

    try:
        ttys = device.find_objects(VTY_REGEX)
        assert len(ttys) > 0
    except AssertionError:
        pytest.fail('No vty lines found')

    for tty in ttys:
        test_val = tty.re_match_iter_typed(required_line, group=0, 
            default="__FAIL__")
        assert test_val!="__FAIL__"
