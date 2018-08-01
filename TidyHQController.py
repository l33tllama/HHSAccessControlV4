from TidyHQOAuthWrapper import TidyHQOAuthWrapper
import sqlite3
import json

class TidyHQController():

    db_name = 'members.db'

    def __init__(self, client_id, client_secret, member_group_id, domain_prefix):
        self.member_group_id = member_group_id
        self.oauth = TidyHQOAuthWrapper(client_id=client_id, client_secret=client_secret, domain_prefix=domain_prefix)
        self.authenticated = False
        self.db = sqlite3.connect(self.db_name)
        self.cursor = self.db.cursor()
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS members (id text PRIMARY KEY,\
        first_name text,
        last_name text,
        rfid integer,
        status text,
        temp_member text);''')

    def connect_to_api(self, username, password):
        self.authenticated = self.oauth.request_api_access_pw(username, password)

    def reload_db(self):
        if not self.authenticated:
            print("Not authenticated! Can't sync DB.")
            return False
        contacts = self.oauth.get_contacts_in_group(self.member_group_id)
        memberships = self.oauth.get_memberships()
        '''u'status': u'active', u'last_name': u'Rodway', u'twitter': u'', u'profile_image': None, 
        u'updated_at': u'2017-10-14T11:51:07+1100', u'postcode': u'',
         u'email_address': u'mrodway@southcom.com.au', u'id': 1670908,
          u'custom_fields': [{u'type': u'string', 
          u'id': u'dd986181c572', u'value': u'3858079', u'title': u'RFID Tag'}], 
          u'city': u'', u'first_name': u'Michael', u'subscribed': True, u'state': None, 
          u'details': None, u'company': u'', u'metadata': None, u'phone_number': u'', 
          u'address1': u'', u'emergency_contact_person': None, u'birthday': None, u'facebook':
           u'', u'nick_name': u'', u'gender': u'', u'created_at': u'2017-01-31T00:42:56+1100', 
           u'emergency_contact_number': None, u'country': None'''
        #fields = ['status', 'last_name', 'twitter', 'profile_image', 'updated_at', 'postcode',
        #'email_address', 'id', 'custom_fields', ]
        if contacts is False or memberships is False:
            #print("Error getting data from TidyHQ!")
            return False
            #print(str(contacts))
        for contact in contacts:
            rfid = 0
            temp_member = False
            #print(str(contact))
            for custom_field in contact['custom_fields']:
                if custom_field['title'] == "RFID Tag":
                    rfid = custom_field['value']
                if custom_field['title'] == "temporary_member":
                    if custom_field['value'] == True:
                        print str(contact)
                        temp_member = True
                        print "Temporary member:"
                        print custom_field['value']
            id = contact["id"]
            first_name = contact["first_name"]
            last_name = contact["last_name"]
            status = "NA"
            for membership in memberships:
                if membership["contact_id"] == id:
                    status = membership['state']
                    
            insert_cmd = 'INSERT or REPLACE INTO members ' +\
            "VALUES ('" + str(id) + "' ,'" +\
            str(first_name) + "', '" +\
            str(last_name) + "', '" +\
            str(rfid) + "', '" +\
            str(status) + "', '" +\
            str(temp_member) + "')"
            print(insert_cmd)
            self.cursor.execute(insert_cmd)
        
        self.cursor.close()
        self.db.commit()
            
        #TODO
    