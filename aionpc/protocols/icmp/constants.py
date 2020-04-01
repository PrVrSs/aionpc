# https://github.com/torvalds/linux/blob/master/include/uapi/linux/icmp.h
# https://www.cymru.com/Documents/ip_icmp.h


ICMP_TYPES = {
    0: 'echo-reply',
    3: 'dest-unreach',
    4: 'source-quench',
    5: 'redirect',
    8: 'echo-request',
    9: 'router-advertisement',
    10: 'router-solicitation',
    11: 'time-exceeded',
    12: 'parameter-problem',
    13: 'timestamp-request',
    14: 'timestamp-reply',
    15: 'information-request',
    16: 'information-response',
    17: 'address-mask-request',
    18: 'address-mask-reply',
    30: 'traceroute',
    31: 'datagram-conversion-error',
    32: 'mobile-host-redirect',
    33: 'ipv6-where-are-you',
    34: 'ipv6-i-am-here',
    35: 'mobile-registration-request',
    36: 'mobile-registration-reply',
    37: 'domain-name-request',
    38: 'domain-name-reply',
    39: 'skip',
    40: 'photuris',
}


ICMP_CODES = {
    3: {
        0: 'network-unreachable',
        1: 'host-unreachable',
        2: 'protocol-unreachable',
        3: 'port-unreachable',
        4: 'fragmentation-needed',
        5: 'source-route-failed',
        6: 'network-unknown',
        7: 'host-unknown',
        9: 'network-prohibited',
        10: 'host-prohibited',
        11: 'TOS-network-unreachable',
        12: 'TOS-host-unreachable',
        13: 'communication-prohibited',
        14: 'host-precedence-violation',
        15: 'precedence-cutoff',
    },
    5: {
        0: 'network-redirect',
        1: 'host-redirect',
        2: 'TOS-network-redirect',
        3: 'TOS-host-redirect',
    },
    11: {
        0: 'ttl-zero-during-transit',
        1: 'ttl-zero-during-reassembly',
    },
    12: {
        0: 'ip-header-bad',
        1: 'required-option-missing',
    },
    40: {
        0: 'bad-spi',
        1: 'authentication-failed',
        2: 'decompression-failed',
        3: 'decryption-failed',
        4: 'need-authentification',
        5: 'need-authorization',
    },
}
