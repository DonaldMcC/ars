import datetime
from plugin_bs_datepicker import bsdatepicker_widget
from plugin_hradio_widget import hradio_widget, hcheckbutton_widget
from plugin_range_widget import range_widget
from plugin_haystack import Haystack
if backend == 'whoosh':
    from plugin_haystack import WhooshBackend
else:
    from plugin_haystack import SimpleBackend
from plugin_location_picker import IS_GEOLOCATION, location_widget


scopes = ['1 National', '2 Regional', '3 Local']


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

db.define_table('download',
                Field('title'),
                Field('download_file', 'upload'),
                Field('description', 'text'),
                Field('download_version', 'string', default='1'),
                format='%(title)s')

db.download.title.requires = IS_NOT_IN_DB(db, db.download.title)

db.define_table('system_scope',
                Field('description', 'string'),
                format='%(description)s')

db.define_table('activity',
                Field('activity', 'string', label="What's happening"),
                Field('details', 'text', label='Details'),
                Field('why', 'text', label='Why are they doing this'),
                Field('fullname', 'string', label='Who'),
                Field('fbid','integer', label='Facebook Id'),
                Field('organisation', label='Organisation Involved (if any)'),
                Field('orgtype', label='Organisation Type', default='Not Known'),
                Field('activescope', 'string', default= '1 Internationl', label='Active Scope',
                      requires=IS_IN_SET(scopes)),
                Field('country', 'reference country', label='country', default=1),
                Field('subdivision', 'reference subdivision', label='area/subdivision', default=1),
                Field('town', 'string', label='Town'),
                Field('coord', 'string', label='Where', comment='Approx location of the activity'),
                Field('activity_long', 'double', default=0.0, label='Latitude', writable=False, readable=False),
                Field('activity_lat', 'double', default=0.0, label='Longitude', writable=False, readable=False),
                Field('auth_userid', 'reference auth_user', writable=False, label='Reporter', default=auth.user_id),
                Field('status', 'string', default='Complete',
                      requires=IS_IN_SET(['Draft', 'Complete',  'Rejected']),
                      comment='Select draft to defer for later editing'),
                Field('activity_time', 'datetime', writable=False, label='When', default=request.utcnow),
                Field('createdate', 'datetime', writable=False, label='Date Created', default=request.utcnow),
                Field('submitdate', 'datetime', writable=False, label='Date Completed'),
                Field('category', 'reference category', default=1, label='Category'),
                Field('rating', 'double', writable=False, label='We feel'),
                Field('impact', 'double', writable=False, label='Importance'),
                Field('tags', 'list:string'),
                Field('numratings', 'integer', default=0),
                Field('numrejects', 'integer', default=0)
                )

db.activity.orgtype.requires=IS_IN_SET(['Corporation', 'Government', 'Not For Profit', 'Other', 'Not Known'])
db.activity.coord.requires = IS_GEOLOCATION()
db.activity.coord.widget = location_widget()


if backend == 'SimpleBackend':
    indsearch = Haystack(db.activity, backend=SimpleBackend)
else:
    indsearch = Haystack(db.activity, backend=WhooshBackend, indexdir='whoosh_' + request.application)
indsearch.indexes('activity', 'details')


db.define_table('image',
                Field('activity', 'reference activity'),
                Field('title', unique=True),
                Field('mediafile', 'upload'),
                format = '%(title)s')

db.define_table('user_rating',
                Field('activityid', db.activity, writable=False ),
                Field('auth_userid', 'reference auth_user', writable=False, readable=False),
                Field('rating', 'integer', label='We feel'),
                Field('impact', 'integer', label='Importance', comment='How many people does this impact'),
                Field('reject', 'boolean', default=False),
                Field('createdate', 'datetime', writable=False, label='Date Created', default=request.utcnow))

#db.user_rating.rating.requires = IS_IN_SET([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
#db.user_rating.rating.requires = IS_IN_SET([1,2])
ratings = ['1 Appalling','2 Very Bad', '3 Bad', '4 Poor', '5 OK', '6 Fine',
           '7 Good', '8 Excellent', '9 Fantastic', '10 Best thing ever']
db.user_rating.rating.requires = IS_IN_SET(ratings)

db.user_rating.rating.widget = hradio_widget

db.user_rating.impact.requires = IS_IN_SET([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
db.user_rating.impact.widget = hradio_widget

db.define_table('viewscope',
                Field('sortorder', 'string', default='1 Priority', label='Sort Order'),
                Field('showscope', 'boolean', label='Show scope Filter', comment='Uncheck to show all'),
                Field('filters', 'string'),
                Field('selection', 'string', default=['Complete']),
                Field('view_scope', 'string', default='1 Global'),
                Field('country', 'reference country', default=1, label='Country'),
                Field('subdivision', 'reference subdivision', default=1, label='Sub-division'),
                Field('showcat', 'boolean', label='Show Category Filter', comment='Uncheck to show all'),
                Field('category', 'reference category', default=1, label='Category'),
                Field('startdate', 'date', default=request.utcnow, label='From Date'),
                Field('enddate', 'date', default=request.utcnow, label='To Date'),
                Field('searchstring', 'string', label='Search:', default=session.searchstring),
                Field('coord', 'string', label='Lat/Longitude'),
                Field('searchrange', 'integer', default=100, label='Search Range in Kilometers'),
                Field('linklevels', 'integer', default=1, label='No of generations of linked items',
                      requires=IS_IN_SET([0,1, 2, 3, 4, 5])))

# default = (session.coord or (auth.user and auth.user.coord))
db.viewscope.view_scope.requires = IS_IN_SET(scopes)
db.viewscope.sortorder.requires = IS_IN_SET(['1 Rating', '2 Importance', '3 Create Date'])
db.viewscope.filters.requires = IS_IN_SET(['Scope', 'Category', 'Date'], multiple=True)
db.viewscope.filters.widget = hcheckbutton_widget
db.viewscope.selection.requires = IS_IN_SET(['Complete', 'Draft'],multiple=True)
db.viewscope.view_scope.widget = hradio_widget
db.viewscope.sortorder.widget = hradio_widget
db.viewscope.searchstring.requires = IS_NOT_EMPTY()
db.viewscope.selection.widget = hcheckbutton_widget

db.viewscope.coord.requires = IS_GEOLOCATION()
db.viewscope.coord.widget = location_widget()

PARAMS = db(db.website_parameters).select().first()