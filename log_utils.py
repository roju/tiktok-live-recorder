import os
import logging.handlers
import time
import sys

class CustomTimedRotatingFileHandler(logging.handlers.TimedRotatingFileHandler):
  def __init__(self, logs_dir):
    self.logs_dir = logs_dir
    filename =  self.logs_dir+time.strftime('%Y-%m-%d')+'.log' #logs_dir must end with os.sep
    logging.handlers.TimedRotatingFileHandler.__init__(self,filename, when='midnight', interval=1, backupCount=0, encoding=None)

  def doRollover(self):
    """
    TimedRotatingFileHandler remix - rotates logs on daily basis, and filename of current logfile is time.strftime("%Y-%m-%d")+".log"
    """ 
    self.stream.close()
    self.baseFilename = self.logs_dir+time.strftime('%Y-%m-%d')+'.log'
    self.stream = open(self.baseFilename, 'w')
    self.rolloverAt = self.rolloverAt + self.interval
    
def config_logging(username, room_id, logs_dir=None):
    """Set up logging handlers"""
    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(
        logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
    handlers=[stream_handler]
    if logs_dir:
        if username: subfolder = username 
        else: subfolder = room_id
        logs_dir = os.path.join(logs_dir, subfolder, '')
        os.makedirs(logs_dir, exist_ok=True)
        file_handler = CustomTimedRotatingFileHandler(logs_dir)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s', datefmt='%H:%M:%S'))
        handlers.append(file_handler)
    logging.basicConfig(level=logging.INFO, handlers=handlers)