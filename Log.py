import logging, logging.handlers
from time import localtime, strftime, sleep
import socket
import httplib, urllib

class FileLogger():
    def __init__(self, log_filename, log_filesize, log_backup_count):
        self.entrant_logger = logging.getLogger('EntrantLogger')
        self.entrant_logger.setLevel(logging.INFO)
        FORMAT = "%(asctime)-15s %(message)s"
        logging.basicConfig(format=FORMAT)
        self.formatter = logging.Formatter("%(asctime)s;%(message)s")

        self.rot_handler = logging.handlers.RotatingFileHandler(log_filename,
                                                                maxBytes=log_filesize,
                                                                backupCount=log_backup_count)
        self.rot_handler.setFormatter(self.formatter)
        self.entrant_logger.addHandler(self.rot_handler)

    def info(self, message):
        self.entrant_logger.info(message)

    def error(self, message):
        self.entrant_logger.error(message)

class PushoverLogger():
    def __init__(self,api_token, user_key, _application):
        self.api_token = api_token
        self.user_key = user_key

    def log(self, message):
        self.send(message, "log")

    def send(self, title, message):
        self.pushnotify_msg(message, title)

    def pushnotify_msg(self, desc, event):
        try:
            conn = httplib.HTTPSConnection("api.pushover.net:443")
            conn.request("POST", "/1/messages.json",
                         urllib.urlencode({
                             "token": self.api_token,
                             "user": self.user_key,
                             "message": desc,
                         }), {"Content-type": "application/x-www-form-urlencoded"})
            conn.getresponse()
        except socket.gaierror as e:
            print e


class Logger():
    def __init__(self, filename, log_filesize, log_backup_count, api_token, user_key, _application):
        self.pushnotify = PushoverLogger(api_token, user_key, _application)
        self.filelogger = FileLogger(filename, log_filesize, log_backup_count)
    def error(self, message):
        self.priority = 2
        self.filelogger.error("HHS Access error: " + message)

    def log(self, message):
        self.priority = 0
        self.filelogger.info("HHS Access: " + message)

    def notify(self, message, title):
        self.pushnotify.pushnotify_msg(message, title)

    def log_and_notify(self, message, title):
        self.filelogger.info(title + ": " + message)
        self.pushnotify.pushnotify_msg(message, title)

    def info(self, message):
        self.filelogger.info(message)
        #self.pushnotify.pushnotify_msg(message, "Info")

    def new_occupant(self, member):
        self.pushnotify.pushnotify_msg(member + " entered the building.", "New occupant")
        self.filelogger.info(member + " entered the building.")

    def alarm_armed(self):
        self.pushnotify.pushnotify_msg("Alarm armed", "alarm armed")
        self.filelogger.info("Alarm armed")

    def alarm_sounding(self):
        self.filelogger.error("Alarm sounding!!")
        self.pushnotify.pushnotify_msg("Alarm is sounding!", "alamr-sounding")

    def invalid_tag(self, rfid_tag, member):
        self.filelogger.error("Invalid tag scanned " + rfid_tag + " " + member)

    def invalid_tag_retries(self, rfid, member):
        self.pushnotify.pushnotify_msg("Multiple invalid tag attempts for " + member , "Multiple tag scans")
        self.filelogger.info("Multiple invalid tag attempts for " + member)