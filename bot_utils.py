import time
import logging
import requests as req
import errors

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Referer': 'https://www.tiktok.com/',
}

def lag_error(err_str) -> bool:
    """Check if ffmpeg output indicates that the stream is lagging"""
    lag_errors = [
        'Server returned 404 Not Found',
        'Stream ends prematurely',
        'Error in the pull function'
    ]
    return any(err in err_str for err in lag_errors)

def retry_wait(seconds=60, print_msg=True):
    """Sleep for the specified number of seconds"""
    if print_msg:
        if seconds < 60:
            logging.info(f'Waiting {seconds} seconds')
        else:
            logging.info(f"Waiting {'%g' % (seconds/60)} minute{'s' if seconds > 60 else ''}")
    time.sleep(seconds)

def check_exists(exp, value):
    """Check if a nested json key exists"""
    # For the case that we have an empty element
    if exp is None:
        return False

    # Check existence of the first key
    if value[0] in exp:
        
        # if this is the last key in the list, then no need to look further
        if len(value) == 1:
            return True
        else:
            next_value = value[1:len(value)]
            return check_exists(exp[value[0]], next_value)
    else:
        return False

def get_proxy_session(proxy_url):
    """Request with TOR or other proxy.
    TOR uses 9050 as the default socks port.
    To (hopefully) prevent getting home IP blacklisted for bot activity.
    """
    try:
        logging.info(f'Using proxy: {proxy_url}')
        session = req.session()
        session.proxies = {'http':  proxy_url, 'https': proxy_url}
        # logging.info("regular ip:")
        # logging.info(req.get("http://httpbin.org/ip").text)
        # logging.info("proxy ip:")
        # logging.info(session.get("http://httpbin.org/ip").text)
        return session
    except Exception as ex:
        logging.error(ex)
        return req

def login_required(json) -> bool:
    # logging.info(json)
    if (check_exists(json, ['data', 'prompts'])
            and 'This account is private' in json['data']['prompts']):
        logging.info('Account is private')
        return True
    elif (check_exists(json, ['status_code'])
            and json['status_code'] == 4003110):
        raise errors.AgeRestricted('Account is age restricted')
    else:
        return False