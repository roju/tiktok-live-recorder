from enum import Enum, IntEnum

class LiveStatus(IntEnum):
    """Enumeration that defines potential states of the live stream"""
    BOT_INIT  = 0
    LAGGING   = 1
    LIVE      = 2
    OFFLINE   = 3


class WaitTime(IntEnum):
    """Enumeration that defines wait times in seconds."""
    LONG  = 120
    SHORT = 60
    LAG   = 5


class StatusCode(IntEnum):
    """Enumeration that defines HTTP status codes."""
    OK          = 200
    REDIRECT    = 302
    BAD_REQUEST = 400


class Mode(IntEnum):
    """Enumeration that represents the recording modes."""
    MANUAL    = 0
    AUTOMATIC = 1


class ErrorMsg(Enum):
    """Enumeration of error messages"""
    def __str__(self):
        return str(self.value)

    BLKLSTD_AUTO_MODE_ERROR: str = 'Automatic mode can be used only in unblacklisted country. Use a VPN\n[*] ' \
                                'Unrestricted country list: ' \
                                'https://github.com/Michele0303/TikTok-Live-Recorder/edit/main/GUIDE.md#unrestricted' \
                                '-country'
    BLKLSTD_ERROR = 'Captcha required or country blocked. Use a vpn or room_id.' \
                 '\nTo get room id: https://github.com/Michele0303/TikTok-Live-Recorder/blob/main/GUIDE.md#how-to-get-room_id' \
                 '\nUnrestricted country list: https://github.com/Michele0303/TikTok-Live-Recorder/edit/main/GUIDE' \
                 '.md#unrestricted-country'
    USERNAME_ERROR = 'Error: Username/Room_id not found or the user has never been in live'
    CONNECTION_CLOSED = 'Connection broken by the server.'


class Info(Enum):
    """Enumeration that defines the version number and the banner message."""
    def __str__(self):
        return str(self.value)

    VERSION = 4.1
    BANNER = f'Tiktok Live Recorder v{VERSION}'
