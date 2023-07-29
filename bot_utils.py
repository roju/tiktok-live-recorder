def lag_error(err_str) -> bool:
    """Check if ffmpeg output indicates that the stream is lagging"""
    lag_errors = [
        'Server returned 404 Not Found',
        'Stream ends prematurely',
        'Error in the pull function'
    ]
    return any(err in err_str for err in lag_errors)
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