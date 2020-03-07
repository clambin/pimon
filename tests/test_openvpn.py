from pimon import OpenVPNProbe


def test_vpn():
    probe = OpenVPNProbe('client.status')
    probe.run()
    assert probe.get_probe('client_tun_tap_read').measured() == 1
    assert probe.get_probe('client_tun_tap_write').measured() == 2
    assert probe.get_probe('client_tcp_udp_read').measured() == 3
    assert probe.get_probe('client_tcp_udp_write').measured() == 4
    assert probe.get_probe('client_auth_read').measured() == 5
    assert probe.get_probe('client_pre_compress').measured() == 6
    assert probe.get_probe('client_post_compress').measured() == 7
    assert probe.get_probe('client_pre_decompress').measured() == 8
    assert probe.get_probe('client_post_decompress').measured() == 9

