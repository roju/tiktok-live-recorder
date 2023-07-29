from browser import BrowserExtractor
        self.browser_exec = browser_exec
        if proxy: self.req = bot_utils.get_proxy_session(proxy)
        else: self.req = req
            if bot_utils.check_exists(json, ['data', 'prompts']):
                if 'This account is private' in json['data']['prompts']:
                    if not self.browser_exec:
                        raise errors.AccountPrivate('Account is private, login required')
                    else:
                        logging.info('Account is private, login required')
                        browser_extractor = BrowserExtractor(self.room_id, self.browser_exec)
                        return browser_extractor.get_live_url()
        except errors.BrowserExtractor as e: raise e
