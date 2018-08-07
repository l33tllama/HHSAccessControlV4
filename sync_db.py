#!/usr/bin/python

import time

import ConfigParser
from Log import Logger
from TidyHQController import TidyHQController

config_filename = 'config.cfg'

class DatabaseSync():
    def __init__(self):
        # Config
        self.config = ConfigParser.RawConfigParser()
        self.config.read(config_filename)

        self.db_reload_seconds = 0
        tidy_client_id = self.config.get('TidyHQ', 'client_id')
        tidy_client_secret = self.config.get('TidyHQ', 'client_secret')
        tidy_member_group = self.config.get('TidyHQ', 'group_id')
        tidy_domain_prefix = self.config.get('TidyHQ', 'domain_prefix')
        self.tidy_username = self.config.get('TidyHQ', 'username')
        self.tidy_password = self.config.get('TidyHQ', 'password')
        self.db_reload_seconds = self.config.getint('TidyHQ', 'update_interval_sec')
        self.push_apikey = self.config.get('Pushover', 'access_token')
        self.push_userkey = self.config.get('Pushover', 'user_key')
        log_filename = self.config.get('Logging', 'sync_filename')
        log_filesize = self.config.get('Logging', 'size_bytes')
        log_backup_count = self.config.get('Logging', 'backup_count')
        #print "Pushover token: " + self.push_apikey

        self.log = Logger(log_filename, log_filesize, log_backup_count, self.push_apikey, self.push_userkey,
                          "HHSAccess")
        self.tidyhq = TidyHQController(tidy_client_id, tidy_client_secret, tidy_member_group, tidy_domain_prefix)

    def reload_db(self):
        self.tidyhq.connect_to_api(self.tidy_username, self.tidy_password)
        if self.tidyhq.reload_db() is False:
            self.log.error("DB update failed!")
        else:
            self.log.log("DB update success")

    def run(self):
        self.reload_db()


if __name__ == '__main__':
    db = DatabaseSync()
    db.run()