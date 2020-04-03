from enum import IntEnum, auto


class ICMPTypes(IntEnum):
    EchoReply = 0
    DestUnreach = 3
    SourceQuench = 4
    Redirect = 5
    EchoRequest = 8
    RouterAdvertisement = 9
    RouterSolicitation = 10
    TimeExceeded = 11
    ParameterProblem = 12
    TimestampRequest = 13
    TimestampReply = 14
    InformationRequest = 15
    InformationResponse = 16
    AddressMaskRequest = 17
    AddressMaskReply = 18
    Traceroute = 30
    DatagramConversionError = 31
    MobileHostRedirect = 32
    Ipv6WhereAreYou = 33
    Ipv6IAmHere = 34
    MobileRegistrationRequest = 35
    MobileRegistrationReply = 36
    DomainNameRequest = 37
    DomainNameReply = 38
    Skip = 39
    Photuris = 40


class IntEnumZeroStart(IntEnum):
    def _generate_next_value_(self, start, count, last_values):
        return count


class ICMPDestUnreachCodes(IntEnumZeroStart):
    NetworkUnreachable = auto()
    HostUnreachable = auto()
    ProtocolUnreachable = auto()
    PortUnreachable = auto()
    FragmentationNeeded = auto()
    SourceRouteFailed = auto()
    NetworkUnknown = auto()
    HostUnknown = auto()
    NetworkProhibited = auto()
    HostProhibited = auto()
    TOSNetworkUnreachable = auto()
    TOSHostUnreachable = auto()
    CommunicationProhibited = auto()
    HostPrecedenceViolation = auto()
    PrecedenceCutoff = auto()


class ICMPRedirectCodes(IntEnumZeroStart):
    NetworkRedirect = auto()
    HostRedirect = auto()
    TOSNetworkRedirect = auto()
    TOSHostRedirect = auto()


class ICMPTimeExceededCodes(IntEnumZeroStart):
    TtlZeroDuringTransit = auto()
    TtlZeroDuringReassembly = auto()


class ICMPParameterProblemCodes(IntEnumZeroStart):
    IpHeaderBad = auto()
    RequiredOptionMissing = auto()


class ICMPPhoturisCodes(IntEnumZeroStart):
    AdSpi = auto()
    AuthenticationFailed = auto()
    DecompressionFailed = auto()
    DecryptionFailed = auto()
    NeedAuthentication = auto()
    NeedAuthorization = auto()
