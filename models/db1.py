
not_empty = IS_NOT_EMPTY()

db.define_table('website_parameters',
                Field('website_name', label=T('Website name'), comment=T('Not currently used')),
                Field('website_init', 'boolean', default=False, label=T('Website Setup'),
                      comment=T('Set to True once initialised')),
                Field('website_title', label=T('Website title'), comment=T('Displayed in title if not blank')),
                Field('website_subtitle', label=T('Website subtitle'), comment=T('Not used')),
                Field('website_url', label=T('Url'), comment=T('URL of the website used for emailing external links')),
                Field('longdesc', 'text', label=T('Long Description'), comment=T('Subject of the website')),
                Field('shortdesc', label=T('Url'), comment=T('Short Description of the website')),
                Field('level1desc', label=T('Level1Desc'), comment=T('First Location Level')),
                Field('level2desc', label=T('Level2Desc'), comment=T('Second Location Level')),
                Field('level3desc', label=T('Level3Desc'), comment=T('Third Location Level')),
                Field('copyright', label=T('Copyright'), default='Has probably been eliminated on more advanced planets'),
                Field('del_answers',  'boolean', default=False, label=T('Delete User Answer on Resolution - not used')),
                Field('force_language', label=T('Force a language (en, it, es, fr, ...)')),
                Field('google_analytics_id', label=T('Google analytics id'),
                      comment=T('Your Google Analytics account ID')),
                Field('seo_website_title', label=T('SEO : Website title'),
                      comment=T('Displayed in <title> tag of the HTML source code')),
                Field('seo_meta_author', label=T('SEO : Meta "author"'),
                      comment=T('Displayed in <meta author> tag of the HTML source code')),
                Field('seo_meta_description', label=T('SEO : Meta "description"'),
                      comment=T('Displayed in <meta description> tag of the HTML source code')),
                Field('seo_meta_keywords', label=T('SEO : Meta "keywords"'),
                      comment=T('Displayed in <meta keywords> tag of the HTML source code')),
                Field('seo_meta_generator', label=T('SEO : Meta "generator"'),
                      comment=T('Displayed in <meta generator> tag of the HTML source code')),
                Field('quests_per_page', 'integer', default=20, label=T('Questions Per Page'),
                      comment=T('Port of the mailserver (used to send email in forms)')),
                Field('comments_per_page', 'integer', default=20, label=T('Comments Per Page'),
                      comment=T('Port of the mailserver (used to send email in forms)')),
                Field('default_resolve_name', 'string', default='Standard', label='Default Resolve Name'))

db.define_table('system_scope',
                Field('description', 'string'),
                format='%(description)s')

db.define_table('category',
                Field('cat_desc', 'string', label='Category',
                      requires=[not_empty, IS_NOT_IN_DB(db, 'category.cat_desc'), IS_LOWER()]),
                Field('categorydesc', 'text', label='Description'),
                format='%(cat_desc)s')

db.define_table('continent',
                Field('continent_name', 'string', label='Continent',
                      requires=[not_empty, IS_SLUG(), IS_NOT_IN_DB(db, 'continent.continent_name')]),
                format='%(continent_name)s')

db.define_table('country',
                Field('country_name', 'string', label='Country',
                      requires=[not_empty, IS_SLUG(), IS_NOT_IN_DB(db, 'country.country_name')]),
                Field('continent', 'string', label='Continent'),
                format='%(country_name)s')

db.define_table('subdivision',
                Field('subdiv_name', 'string', label='Sub-division'),
                Field('country', 'string'),
                format='%(subdiv_name)s')

db.define_table('activity',
                Field('activity', 'string', label='Activity'),
                Field('details', 'text', label='Details'),
                Field('forename', 'string', label='First Name'),
                Field('surname', label='Surname'),
                Field('organisation', label='Organisation'),
                Field('orgtype', label='Organisation Type'),
                Field('town', label='nearest town or city'),
                Field('subdivision', label='area/subdivision'),
                Field('country', label='country'),
                Field('continent', label='continent'),
                Field('coord', 'string', label='Lat/Longitude'),
                Field('question_long', 'double', default=0.0, label='Latitude', writable=False, readable=False),
                Field('question_lat', 'double', default=0.0, label='Longitude', writable=False, readable=False),
                Field('auth_userid', 'reference auth_user', writable=False, label='Submitter', default=auth.user_id),
                Field('status', 'string', default='In Progress',
                      requires=IS_IN_SET(['Draft', 'Complete',  'Rejected']),
                      comment='Select draft to defer for later editing'),
                Field('createdate', 'datetime', writable=False, label='Date Created', default=request.utcnow),
                Field('submitdate', 'datetime', writable=False, label='Date Completed'),
                Field('category', 'string', default='Unspecified', label='Category'),
                Field('rating', 'decimal(6,2)', default=5, writable=False, label='We feel'),
                Field('impact', 'decimal(6,2)', default=5, writable=False, label='Importance'),
                Field('tags', 'list:string'),
                Field('numratings', 'integer', default=0)
                )

db.define_table('user_rating',
                Field('activityid', db.activity, writable=False ),
                Field('auth_userid', 'reference auth_user', writable=False, readable=False),
                Field('rating', 'decimal(6,2)', default=5, writable=False, label='We feel'),
                Field('impact', 'decimal(6,2)', default=5, writable=False, label='Importance'),
                Field('reject', 'boolean', default=False),
                Field('createdate', 'datetime', writable=False, label='Date Created', default=request.utcnow))
                
                
if not init:
    if db(db.continent.continent_name == "Unspecified").isempty():
        contid = db.continent.insert(continent_name="Unspecified")

