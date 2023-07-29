import logging
import logging.handlers
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
                        help='When recording ends, concatenate all video files into a single file. Requires ffmpeg.',
                        action='store_true')
    parser.add_argument('-store_logs',
                        nargs='?',
                        default=None,
                        const='./logs',
                        help="Log console output to a file named with today's date in the specified folder",
                        action='store')
    if args.combine and not args.ffmpeg:
        raise Exception('To use combine function, add -ffmpeg flag.')
def config_logging(logs_dir=None):
    """Set up logging handlers"""
    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(
        logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
    handlers=[stream_handler]
    if logs_dir:
        os.makedirs(logs_dir, exist_ok=True)
        log_file = os.path.join(logs_dir, f'{datetime.date.today()}.log')
        file_handler = logging.handlers.TimedRotatingFileHandler(
            filename=log_file, when="midnight")
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s', datefmt="%H:%M:%S"))
        handlers.append(file_handler)
    logging.basicConfig(level=logging.INFO, handlers=handlers)
        config_logging(args.store_logs)
            proxy=args.proxy,
            browser_exec=args.browser_exec,
            combine=args.combine
