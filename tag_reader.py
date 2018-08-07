import ConfigParser, time
from Log import Logger
from DoorController import DoorController as dc
from SQLiteDB import SQLiteDB as sdb


class TagReader():
    config_filename = "config.cfg"

    def __init__(self):

        self.last_tag_scanned = 0
        self.tag_scan_count = 0
        self.tag_scan_repeat_message = 3

        self.config = ConfigParser.RawConfigParser()
        self.config.read(self.config_filename)
        self.push_apikey = self.config.get('Pushover', 'access_token')
        self.push_userkey = self.config.get('Pushover', 'user_key')
        log_filename = self.config.get('Logging', 'tag_filename')
        log_filesize = self.config.get('Logging', 'size_bytes')
        log_backup_count = self.config.get('Logging', 'backup_count')
        self.log = Logger(log_filename, log_filesize, log_backup_count, self.push_apikey, self.push_userkey, "HHSAccess")
        debug_nopigpio = self.config.getboolean('Debug', 'nopigpio')

        self.dc = dc(nopigpio=debug_nopigpio)
        self.dc.set_tag_scanned_callback(self.tag_scanned)
        self.dc.set_alarm_sounding_callback(self.alarm_sounding)
        self.dc.set_alarm_armed_callback(self.alarm_armed)
        self.db = sdb("members.db")
        self.log.log_and_notify("Startup completed", "System startup")
        #member, is_allowed = self.db.is_allowed(39160494)
        #self.tag_scanned(0, 39163864)
        #print str((member, is_allowed))

    def unlock_door(self, contact_name):
        self.tag_scan_count = 0
        self.dc.unlock_door()
        self.log.new_occupant(contact_name)
        pass

    def open_door(self, contact_name):
        self.tag_scan_count = 0
        self.dc.unlock_door()
        self.log.new_occupant(contact_name)

    def tag_scanned(self, bits, rfid):
        self.log.info("Tag scanned: " + str(rfid))
        contact, is_allowed = self.db.is_allowed(rfid)
        print contact, is_allowed
        contact_name = "Unknown"
        if contact is not None:
            contact_name = str(contact[1]) + " " + str(contact[2])
            info_str = "Contact found: " + contact_name

            if is_allowed is True:
                info_str += " - allowed."
            else:
                info_str += " - not allowed."
            self.log.info(info_str)
            if is_allowed: self.open_door(contact_name)
        else:
            self.log.info("Unknown ID.")

        if not is_allowed:
            self.log.invalid_tag_retries(rfid, contact_name)

            # Cheack for repeat scans
            if(rfid == self.last_tag_scanned):
                self.tag_scan_count += 1
                if(self.tag_scan_count >= self.tag_scan_repeat_message):
                    self.log.invalid_tag_retries(rfid, contact_name)
            else:
                self.tag_scan_count = 0
            self.last_tag_scanned = rfid
        pass

    def alarm_sounding(self):
        self.log.alarm_sounding()
        pass

    def alarm_armed(self):
        self.log.alarm_armed()
        pass

    def reload_db(self):
        pass

    def run(self):
        while(True):
            time.sleep(30*60*60)
            self.log.info("Heartbeat")


if __name__ == '__main__':
    tr = TagReader()
    tr.run()