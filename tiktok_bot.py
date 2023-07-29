from browser import BrowserExtractor
        self.browser_exec = browser_exec
        self.combine = combine
        if proxy: self.req = bot_utils.get_proxy_session(proxy)
        else: self.req = req
        self.out_file = None
        self.video_list = []
                if self.status == LiveStatus.LAGGING:
                    bot_utils.retry_wait(WaitTime.LAG, False)
                elif self.status == LiveStatus.LAGGING:
                    live_url = self.get_live_url()
                    self.start_recording(live_url)
            except (errors.GenericReq, ValueError, req.HTTPError, 
                    errors.BrowserExtractor, errors.ConnectionClosed, 
                    errors.UserNotFound) as e:
                if self.mode == Mode.MANUAL: raise e
                else: 
                    logging.error(e)
                    self.room_id = None
                    bot_utils.retry_wait(WaitTime.SHORT)
            except errors.Blacklisted as e:
                if Mode == Mode.AUTOMATIC:
                    logging.error(ErrorMsg.BLKLSTD_AUTO_MODE_ERROR)
                else:
                    logging.error(ErrorMsg.BLKLSTD_ERROR)
                raise e
        if self.status is not LiveStatus.LAGGING:
            logging.info(f"Output directory: {self.out_dir}")
                            self.status = LiveStatus.LIVE
                if not should_exit: raise errors.StreamLagging
        except errors.StreamLagging:
            logging.info('Stream lagging')
        self.status = LiveStatus.LAGGING

        try:
            if os.path.getsize(self.out_file) < 1000000:
                os.remove(self.out_file)
                # logging.info('removed file < 1MB')
            else:
                self.video_list.append(self.out_file)
        except FileNotFoundError: pass
        except Exception as e: logging.error(e)
                            self.status = LiveStatus.LIVE
                    else:
                        # logging.error(line.strip())
                        ffmpeg_err = ffmpeg_err + ''.join(line)
            if ffmpeg_err: 
                if bot_utils.lag_error(ffmpeg_err): raise errors.StreamLagging
                else: raise errors.FFmpeg(ffmpeg_err.strip())
    """
 ███████ ██ ███    ██ ██ ███████ ██   ██     ██████  ███████  ██████ 
 ██      ██ ████   ██ ██ ██      ██   ██     ██   ██ ██      ██      
 █████   ██ ██ ██  ██ ██ ███████ ███████     ██████  █████   ██      
 ██      ██ ██  ██ ██ ██      ██ ██   ██     ██   ██ ██      ██      
 ██      ██ ██   ████ ██ ███████ ██   ██     ██   ██ ███████  ██████ 
    """

    def finish_recording(self):
        """Combine multiple videos into one if needed"""
        try:
            if self.combine and len(self.video_list) > 1:
                current_date = time.strftime('%Y.%m.%d_%H-%M-%S', time.localtime())
                self.out_file = f'{self.out_dir}TK_{self.user}_{current_date}_concat.mp4'
                logging.info(f'Concatenating {len(self.video_list)} video files')
                with open(f'{self.out_dir}concat.txt', 'w') as file:
                    for v in self.video_list: file.write(f"file '{v}'\n")
                (ffmpeg.input(f'{self.out_dir}concat.txt', **{'f': 'concat'}, **{'safe': 0})
                .output(self.out_file, c='copy')
                .run(quiet=True))
                os.remove(f'{self.out_dir}concat.txt')
                for v in self.video_list: os.remove(v)
            if os.path.isfile(self.out_file):
                logging.info(f'Recording finished: {self.out_file}\n')
        except Exception as ex: logging.error(ex)
        self.video_list = []
        self.out_file = None
            json = self.req.get(url, headers=bot_utils.headers).json()
            # logging.info(f'is_user_live response {json}')
            if not bot_utils.check_exists(json, ['LiveRoomInfo', 'status']):
                raise ValueError(f'LiveRoomInfo.status not found in json: {json}')
            live_status_code = json['LiveRoomInfo']['status']
            if live_status_code != 4: return (LiveStatus.LAGGING 
                if self.status == LiveStatus.LAGGING else LiveStatus.LIVE)
            
        except ConnectionAbortedError:
            raise errors.ConnectionClosed(ErrorMsg.CONNECTION_CLOSED)
        except ValueError as e: raise e
        except Exception as ex:
            raise errors.GenericReq(ex)
            if self.status is not LiveStatus.LAGGING:
                logging.info(f'Getting live url for room ID {self.room_id}')
            json = self.req.get(url, headers=bot_utils.headers).json()
            if bot_utils.check_exists(json, ['data', 'prompts']):
                if 'This account is private' in json['data']['prompts']:
                    if not self.browser_exec:
                        raise errors.AccountPrivate('Account is private, login required')
                    else:
                        logging.info('Account is private, login required')
                        browser_extractor = BrowserExtractor(self.room_id, self.browser_exec)
                        return browser_extractor.get_live_url()
            if not bot_utils.check_exists(json, ['data', 'stream_url', 'rtmp_pull_url']):
                raise ValueError(f'rtmp_pull_url not in response: {json}')
            return json['data']['stream_url']['rtmp_pull_url']
        except ValueError as e: raise e
        except errors.AccountPrivate as e: raise e
        except errors.BrowserExtractor as e: raise e
        except Exception as ex:
            raise errors.GenericReq(ex)
            if response.status_code == StatusCode.REDIRECT:
                raise errors.Blacklisted('Redirect')
            if not match: raise ValueError('room_id not found')
        except (req.HTTPError, errors.Blacklisted) as e:
            raise errors.Blacklisted(e)
        except AttributeError as e:
            raise errors.UserNotFound(f'{ErrorMsg.USERNAME_ERROR}\n{e}')
        except ValueError as e: raise e
        except Exception as ex:
            raise errors.GenericReq(ex)
            json = req.get(url, headers=bot_utils.headers).json()
            if not bot_utils.check_exists(json, ['LiveRoomInfo', 'ownerInfo', 'uniqueId']):
                logging.error(f'LiveRoomInfo.uniqueId not found in json: {json}')
                raise errors.UserNotFound(ErrorMsg.USERNAME_ERROR)
            return json['LiveRoomInfo']['ownerInfo']['uniqueId']
            
        except ConnectionAbortedError:
            raise errors.ConnectionClosed(ErrorMsg.CONNECTION_CLOSED)
        except errors.UserNotFound as e: raise e
        except Exception as ex:
            raise errors.GenericReq(ex)