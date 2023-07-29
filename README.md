<div align="center">

# TikTok Live Recorder 🎥

A CLI tool for recording TikTok live streams

</div>

## How To Use
  
To clone and run this application, you'll need [Git](https://git-scm.com) and [Python3](https://www.python.org/downloads/) installed on your computer. From your command line:

1. Clone this repository
```bash
git clone https://github.com/roju/tiktok-live-recorder && cd tiktok-live-recorder
```
2. Install dependencies
```bash
pip install -r requirements.txt
```
3. Run the app
```bash
python ttlr.py -h
```

### Recording Private Streams
  
Recording private streams is supported via web browser with a helper extension installed. This is an experimental feature.

1. Install Google Chrome or other browser supported by the extension
2. Install the extension from the browser-extension folder
3. In the browser, log in to your TikTok account which has permission to view the private stream
4. Run ttlr.py using the browser_exec argument, specifying the path to your browser executable

### Proxy Server

In automatic mode, we make many repeated requests at a fixed interval. TikTok may at some point in the future decide to flag such requests as bot activity and blacklist your IP (this assumption is purely speculative at this point). Also, you may be able to bypass restrictions in certain countries (untested). The proxy is only used for certian requests, not for downloading the video data.

Use the -proxy argument to specify a proxy server. Defaults to tor proxy which requires tor to be installed and confirured on your system.

## To-Do List
- [x] Record private live streams with browser extension
- [x] Handle stream lagging and interruptions
- [x] Log console output to file
- [x] Automatic Recording
- [x] Recording by room_id
- [x] Using proxy to avoid bot detection
- [x] Using proxy to bypass login restriction in some country. (only to get the room_id)
- [ ] Recording by tiktok live url
- [ ] Add feature to send recorded live streams to Telegram via Telegram bot

## Legal
This code is in no way affiliated with, authorized, maintained, sponsored or endorsed by TikTok or any of its affiliates or subsidiaries. Use at your own risk.

