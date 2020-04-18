import pytest
from pimon.openvpn import OpenVPNProbe


def test_vpn():
    probe = OpenVPNProbe('client.status')
    probe.run()
    measured = probe.measured()
    assert measured['client_tun_tap_read'] == 1
    assert measured['client_tun_tap_write'] == 2
    assert measured['client_tcp_udp_read'] == 3
    assert measured['client_tcp_udp_write'] == 4
    assert measured['client_auth_read'] == 5
    assert measured['client_pre_compress'] == 6
    assert measured['client_post_compress'] == 7
    assert measured['client_pre_decompress'] == 8
    assert measured['client_post_decompress'] == 9


def test_bad_file():
    with pytest.raises(FileNotFoundError):
        probe = OpenVPNProbe('notafile')