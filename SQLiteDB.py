import sqlite3

class SQLiteDB:
    def __init__(self, database_file):
        self.db_name = database_file

    def is_allowed(self, rfid):
        conn = sqlite3.connect(self.db_name)
        cur = conn.cursor()
        cur.execute('select * from members where rfid is ' + str(rfid))
        member = cur.fetchone()
        # if active member or temp_member (hack)
        if member[4] == 'activated' or member[5] == 'True':
            return (member, True)
        else:
            return (None, False)

        print str(member[4])
        print str(member)