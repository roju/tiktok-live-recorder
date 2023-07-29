<div align="center">

# TikTok Live Recorder🎥

TikTok Live Recorder is a simple **tiktok live streaming recorder**.

<img src="/assets/sample.png" width="650px">
</div>

<!--
## Requirements
<a href="https://streamlink.github.io/install.html">Install StreamLink</a>
-->

## How To Use
  
To clone and run this application, you'll need [Git](https://git-scm.com) and [Python3](https://www.python.org/downloads/) installed on your computer. From your command line:

```bash
# Clone this repository
$ git clone https://github.com/Michele0303/TikTok-Live-Recorder
# Go into the repository
$ cd TikTok-Live-Recorder
# Install dependencies
$ pip install -r requirements.txt
# Run the app
$ python main.py -h
```
### Proxy Server

In automatic mode, we make many repeated requests at a fixed interval. TikTok may at some point in the future decide to flag such requests as bot activity and blacklist your IP (this assumption is purely speculative at this point). Also, you may be able to bypass restrictions in certain countries (untested). The proxy is only used for certian requests, not for downloading the video data.

Use the -proxy argument to specify a proxy server. Defaults to tor proxy which requires tor to be installed and confirured on your system.

## To-Do List
- [x] Log console output to file
- [x] Automatic Recording
- [x] Recording by room_id
- [x] Using proxy to avoid bot detection
- [x] Using proxy to bypass login restriction in some country. (only to get the room_id)
- [ ] Improve the graphical user interface
- [ ] Add feature to send recorded live streams to Telegram via Telegram bot

## Legal
This code is in no way affiliated with, authorized, maintained, sponsored or endorsed by TikTok or any of its affiliates or subsidiaries. Use at your own risk.

