        if proxy: self.req = bot_utils.get_proxy_session(proxy)
        else: self.req = req
