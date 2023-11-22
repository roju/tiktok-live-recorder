import argparse
import logging
import log_utils
import os
import traceback
from enums import Mode, Info
from tiktok_bot import TikTok


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('-user',
                        help='Record a live from the username',
                        action='store')
    parser.add_argument('-room_id',
                        help='Record a live from the room_id',
                        action='store')
    parser.add_argument('-mode',
                        default='manual',
                        help='Recording mode: (manual,auto) [Default: manual]\n[manual] => manual live recording\n[auto] => automatic live recording when the user is in live',
                        action='store')
    parser.add_argument('-out_dir',
                        help='Output directory where video files will be stored',
                        default=os.path.dirname(os.path.abspath(__file__)),
                        action='store')
    parser.add_argument('-ffmpeg',
                        help='Record via FFmpeg; allows real-time conversion to mp4 and video file concatenation',
                        action='store_true')
    parser.add_argument('-duration',
                        help='Stop recording the live after this number of seconds [Default: None]',
                        type=int,
                        default=None,
                        action='store')
    parser.add_argument('-proxy',
                        nargs='?',
                        default=None,
                        const='socks5://127.0.0.1:9050',
                        help='Route repetitive requests through a proxy server',
                        action='store')
    parser.add_argument('-browser_exec',
                        nargs='?',
                        default=None,
                        const='/usr/bin/google-chrome-stable',
                        help='Path to browser executable for recording private streams',
                        action='store')
    parser.add_argument('-combine',
                        help='When recording ends, concatenate all video files into a single file. Requires ffmpeg',
                        action='store_true')
    parser.add_argument('-delete_segments',
                        help='Delete redundant video segment files after successful concat. Requires -combine option',
                        action='store_true')
    parser.add_argument('-store_logs',
                        nargs='?',
                        default=None,
                        const='./logs',
                        help="Log console output to a file named with today's date in the specified folder",
                        action='store')

    args = parser.parse_args()
    if not args.user and not args.room_id:
        raise Exception('Missing user/room_id value')
    if args.room_id: args.room_id = str(args.room_id)
    if args.mode != 'manual' and args.mode != 'auto':
        raise Exception('-mode value must be either "manual" or "auto"')
    if args.mode == 'manual':
        args.mode = Mode.MANUAL
    else:
        args.mode = Mode.AUTOMATIC
        if not args.ffmpeg:
            raise Exception('To use automatic recording mode, add -ffmpeg flag.')
    if (args.out_dir != '' and isinstance(args.out_dir, str)
            and not (args.out_dir.endswith('/') or args.out_dir.endswith('\\'))):
        if os.name == 'nt':
            args.out_dir = args.out_dir + '\\'
        else:
            args.out_dir = args.out_dir + '/'
    if args.combine and not args.ffmpeg:
        raise Exception('To use combine function, add -ffmpeg flag.')
    if args.delete_segments and not args.combine:
        raise Exception('To use delete_segments function, add -combine flag.')
    if args.duration is not None and args.duration < 0:
        raise Exception('Duration must be a positive number')
    return args

def main():
    try:
        args = parse_args()
        log_utils.config_logging(args.user, args.room_id, args.store_logs)
        logging.info(Info.BANNER)
        bot = TikTok(
            out_dir=args.out_dir,
            mode=args.mode,
            user=args.user,
            room_id=args.room_id,
            use_ffmpeg=args.ffmpeg,
            proxy=args.proxy,
            duration=args.duration,
            browser_exec=args.browser_exec,
            combine=args.combine,
            delete_segments=args.delete_segments
        )
        bot.run()
    except Exception as ex:
        logging.error('Exception caught in main:')
        logging.error(f'{ex}\n')
        traceback.print_exc()

if __name__ == '__main__':
    main()
