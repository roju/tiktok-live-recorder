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