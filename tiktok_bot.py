import time
import requests as req
import re
import ffmpeg
import sys
import os
import logging
import bot_utils
import errors
import io
import shutil
from enums import Mode, ErrorMsg, StatusCode, WaitTime, LiveStatus
from browser import BrowserExtractor


class TikTok:

    def __init__(self, out_dir, mode=Mode.MANUAL, user=None, room_id=None,
                 use_ffmpeg=None, proxy=None, duration=None, browser_exec=None,
                 combine=None, delete_segments=None):
        self.out_dir = out_dir
        self.mode = mode
        self.user = user
        self.room_id = room_id
        self.use_ffmpeg = use_ffmpeg
        self.duration = duration
        self.browser_exec = browser_exec
        self.combine = combine
        self.delete_segments = delete_segments
        if proxy: self.req = bot_utils.get_proxy_session(proxy)
        else: self.req = req
        self.status = LiveStatus.BOT_INIT
        self.out_file = None
        self.video_list = []

    def run(self):
        """Runs the program in the selected mode.

        If the mode is MANUAL, it checks if the user is currently live and if so, starts recording.
        If the mode is AUTOMATIC, it continuously checks if the user is live and if not, waits for the specified timeout before rechecking.
        If the user is live, it starts recording.
        """
        while True:
            try:
                if self.status == LiveStatus.LAGGING:
                    bot_utils.retry_wait(WaitTime.LAG, False)
                if self.room_id is None:
                    self.room_id = self.get_room_id_from_user()
                if self.user is None:
                    self.user = self.get_user_from_room_id()
                if self.status == LiveStatus.BOT_INIT:
                    logging.info(f'Username: {self.user}')
                    logging.info(f'Room ID: {self.room_id}')

                self.status = self.is_user_live()

                if self.status == LiveStatus.OFFLINE:
                    logging.info(f'{self.user} is offline')
                    self.room_id = None
                    if self.out_file:
                        self.finish_recording()
                    if self.mode == Mode.MANUAL: exit(0)
                    else:
                        bot_utils.retry_wait(WaitTime.LONG, False)
                elif self.status == LiveStatus.LAGGING:
                    live_url = self.get_live_url()
                    self.start_recording(live_url)
                elif self.status == LiveStatus.LIVE:
                    logging.info(f'{self.user} is live')
                    live_url = self.get_live_url()
                    logging.info(f'Live URL: {live_url}')
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
            except KeyboardInterrupt:
                logging.info('Stopped by keyboard interrupt\n')
                sys.exit(0)

    def start_recording(self, live_url):
        """Start recording live"""
        should_exit = False
        current_date = time.strftime('%Y.%m.%d_%H-%M-%S', time.localtime())
        suffix = '' if self.use_ffmpeg else '_flv'
        self.out_file = f'{self.out_dir}{self.user}_{current_date}{suffix}.mp4'
        if self.status is not LiveStatus.LAGGING:
            logging.info(f"Output directory: {self.out_dir}")
        try:
            if self.use_ffmpeg:
                self.handle_recording_ffmpeg(live_url)
                if self.duration is not None: should_exit = True
            else:
                response = req.get(live_url, stream=True)
                with open(self.out_file, 'wb') as file:
                    start_time = time.time()
                    rec_started = False
                    for chunk in response.iter_content(chunk_size=4096):
                        file.write(chunk)
                        if not rec_started:
                            rec_started = True
                            self.status = LiveStatus.LIVE
                            logging.info(f"Started recording{f' for {self.duration} seconds' if self.duration else ''}")
                            print('Press CTRL + C to stop')
                        elapsed_time = time.time() - start_time
                        if self.duration is not None and elapsed_time >= self.duration:
                            should_exit = True
                            break
                if not should_exit: raise errors.StreamLagging

        except errors.StreamLagging:
            logging.info('Stream lagging')
        except errors.FFmpeg as e:
            logging.error('FFmpeg error:')
            logging.error(e)
        except FileNotFoundError as e:
            logging.error('FFmpeg is not installed.')
            raise e
        except KeyboardInterrupt:
            logging.info('Recording stopped by keyboard interrupt')
            should_exit = True
        except Exception as e:
            logging.error(f'Recording error: {e}')

        self.status = LiveStatus.LAGGING

        try:
            if os.path.getsize(self.out_file) < 1000000:
                os.remove(self.out_file)
                # logging.info('removed file < 1MB')
            else:
                self.video_list.append(self.out_file)
        except FileNotFoundError: pass
        except Exception as e: logging.error(e)

        if should_exit:
            self.finish_recording()
            sys.exit(0)

    def handle_recording_ffmpeg(self, live_url):
        """Show real-time stats and raise ffmpeg errors"""
        stream = ffmpeg.input(live_url, **{'loglevel': 'error'}, **{'reconnect': 1},
                              **{'reconnect_streamed': 1}, **{'reconnect_at_eof': 1},
                              **{'reconnect_delay_max': 5}, **{'timeout': 10000000}, stats=None)
        stats_shown = False
        if self.duration is not None:
            stream = ffmpeg.output(stream, self.out_file, c='copy', t=self.duration)
        else:
            stream = ffmpeg.output(stream, self.out_file, c='copy')
        try:
            proc = ffmpeg.run_async(stream, pipe_stderr=True)
            ffmpeg_err = ''
            last_stats = ''
            text_stream = io.TextIOWrapper(proc.stderr, encoding="utf-8")
            while True:
                if proc.poll() is not None: break
                for line in text_stream:
                    line = line.strip()
                    if 'frame=' in line:
                        last_stats = line
                        if not stats_shown:
                            logging.info(f"Started recording{f' for {self.duration} seconds' if self.duration else ''}")
                            print("Press 'q' to re-start recording, CTRL + C to stop")
                            self.status = LiveStatus.LIVE
                        print(last_stats, end='\r')
                        stats_shown = True
                    else:
                        ffmpeg_err = ffmpeg_err + ''.join(line)
            if ffmpeg_err:
                if bot_utils.lag_error(ffmpeg_err): raise errors.StreamLagging
                else: raise errors.FFmpeg(ffmpeg_err.strip())
        except KeyboardInterrupt as i: raise i
        except ValueError as e: logging.error(e)
        finally:
            if stats_shown: logging.info(last_stats)

    def finish_recording(self):
        """Combine multiple videos into one if needed"""
        try:
            current_date = time.strftime('%Y.%m.%d_%H-%M-%S', time.localtime())
            ffmpeg_concat_list = f'{self.user}_{current_date}_concat_list.txt'
            if self.combine and len(self.video_list) > 1:
                self.out_file = f'{self.out_dir}{self.user}_{current_date}_concat.mp4'
                logging.info(f'Concatenating {len(self.video_list)} video files')
                with open(ffmpeg_concat_list, 'w') as file:
                    for v in self.video_list: file.write(f"file '{v}'\n")
                stream = ffmpeg.input(ffmpeg_concat_list, **{'f': 'concat'}, **{'safe': 0}, **{'loglevel': 'error'})
                stream = ffmpeg.output(stream, self.out_file, c='copy')
                proc = ffmpeg.run_async(stream, pipe_stderr=True)
                text_stream = io.TextIOWrapper(proc.stderr, encoding="utf-8")
                ffmpeg_err = ''
                while True:
                    if proc.poll() is not None: break
                    for line in text_stream: ffmpeg_err = ffmpeg_err + ''.join(line)
                if ffmpeg_err:
                    raise errors.FFmpeg(ffmpeg_err.strip())
                logging.info(f'Concat finished')
                if self.delete_segments:
                    for v in self.video_list: os.remove(v)
                    logging.info(f'Deleted {len(self.video_list)} video files')
                else:
                    videos_dir = os.path.join(self.out_dir, f'{self.user}_{current_date}_segments', '')
                    os.makedirs(videos_dir)
                    for v in self.video_list: shutil.move(v, videos_dir)
                    logging.info(f'Moved recorded segments to directory: {videos_dir}')
            if os.path.isfile(self.out_file):
                logging.info(f'Recording finished: {self.out_file}\n')
            if os.path.isfile(ffmpeg_concat_list):
                os.remove(ffmpeg_concat_list)
        except errors.FFmpeg as e:
            logging.error('FFmpeg concat error:')
            logging.error(e)
        except Exception as ex: logging.error(ex)
        self.video_list = []
        self.out_file = None

    def is_user_live(self) -> LiveStatus:
        """Check whether the user is live"""
        try:
            url = f'https://www.tiktok.com/api/live/detail/?aid=1988&roomID={self.room_id}'
            json = self.req.get(url, headers=bot_utils.headers).json()
            # logging.info(f'is_user_live response {json}')
            if not bot_utils.check_exists(json, ['LiveRoomInfo', 'status']):
                raise ValueError(f'LiveRoomInfo.status not found in json: {json}')
            live_status_code = json['LiveRoomInfo']['status']
            if live_status_code != 4: return (LiveStatus.LAGGING
                if self.status == LiveStatus.LAGGING else LiveStatus.LIVE)
            else: return LiveStatus.OFFLINE

        except ConnectionAbortedError:
            raise errors.ConnectionClosed(ErrorMsg.CONNECTION_CLOSED)
        except ValueError as e: raise e
        except Exception as ex:
            raise errors.GenericReq(ex)

    def get_live_url(self) -> str:
        """Get the cdn (flv or m3u8) of the stream"""
        try:
            if self.status is not LiveStatus.LAGGING:
                logging.info(f'Getting live url for room ID {self.room_id}')
            url = f'https://webcast.tiktok.com/webcast/room/info/?aid=1988&room_id={self.room_id}'
            json = self.req.get(url, headers=bot_utils.headers).json()
            if bot_utils.login_required(json):
                if not self.browser_exec:
                    raise errors.LoginRequired('Login required')
                else:
                    logging.info('Login required')
                    browser_extractor = BrowserExtractor()
                    return browser_extractor.get_live_url(self.room_id, self.browser_exec)
            if not bot_utils.check_exists(json, ['data', 'stream_url', 'rtmp_pull_url']):
                raise ValueError(f'rtmp_pull_url not in response: {json}')
            return json['data']['stream_url']['rtmp_pull_url']
        except ValueError as e: raise e
        except errors.LoginRequired as e: raise e
        except errors.AgeRestricted as e: raise e
        except errors.BrowserExtractor as e: raise e
        except Exception as ex:
            raise errors.GenericReq(ex)

    def get_room_id_from_user(self) -> str:
        """Given a username, get the room_id"""
        try:
            response = self.req.get(
                f'https://www.tiktok.com/@{self.user}/live',
                allow_redirects=False, headers=bot_utils.headers)
            # logging.info(f'get_room_id_from_user response: {response.text}')
            if response.status_code == StatusCode.REDIRECT:
                raise errors.Blacklisted('Redirect')
            match = re.search(r'"roomId":"(\d+)"', response.text)
            if not match: raise ValueError('roomId not found')
            return match.group(1)

        except (req.HTTPError, errors.Blacklisted) as e:
            raise errors.Blacklisted(e)
        except AttributeError as e:
            raise errors.UserNotFound(f'{ErrorMsg.USERNAME_ERROR}\n{e}')
        except ValueError as e: raise e
        except Exception as ex:
            raise errors.GenericReq(ex)

    def get_user_from_room_id(self) -> str:
        """Given a room_id, get the username"""
        try:
            url = f'https://www.tiktok.com/api/live/detail/?aid=1988&roomID={self.room_id}'
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