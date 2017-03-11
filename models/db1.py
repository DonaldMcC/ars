

db.define_table('activity',
                Field('activity', 'string', label='Activity'),
                Field('forename', 'string', label='First Name'),
                Field('surname', label='surname'),
                Field('addr1', label='address 1'),
                Field('addr2', label='address 2'),
                Field('addr3', label='address 3'),
                Field('addr4', label='address 4'),
                )
