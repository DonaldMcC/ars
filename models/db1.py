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
                Field('activity', 'string', label="What's happening"),
                Field('details', 'text', label='Details'),
                Field('why', 'text', label='Why are they doing this'),
                Field('fullname', 'string', label='Who'),
                Field('fbid','integer', label='Facebook Id'),
                Field('organisation', label='Organisation Involved (if any)'),
                Field('orgtype', label='Organisation Type', default='Not Known'),
                Field('town', label='town/city where the person is based'),
                Field('subdivision', 'reference subdivision', label='area/subdivision', default=3),
                Field('country', 'reference country', label='country', default=1),
                Field('activity_scope', 'string', label='Activity Scope'),
                Field('diff_locn', 'boolean', label='Check if activity at different location'),
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
                Field('rating', 'decimal(6,2)', default=5, writable=False, label='We feel'),
                Field('impact', 'decimal(6,2)', default=5, writable=False, label='Importance'),
                Field('tags', 'list:string'),
                Field('numratings', 'integer', default=0),
                Field('numimpacts', 'integer', default=0),
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
                Field('impact', 'decimal(6,2)', label='Importance', comment='How many people does this impact'),
                Field('reject', 'boolean', default=False),
                Field('createdate', 'datetime', writable=False, label='Date Created', default=request.utcnow))

db.user_rating.rating.requires = IS_IN_SET([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
db.user_rating.rating.widget = hradio_widget

db.user_rating.impact.requires = IS_IN_SET([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
db.user_rating.impact.widget = hradio_widget

scopes = ['1 Global', '2 Continental', '3 National', '4 Provincial', '5 Local']
db.define_table('viewscope',
                Field('sortorder', 'string', default='1 Priority', label='Sort Order'),
                Field('showscope', 'boolean', label='Show scope Filter', comment='Uncheck to show all'),
                Field('filters', 'string'),
                Field('view_scope', 'string', default='1 Global'),
                Field('continent', 'string', default='Unspecified', label='Continent'),
                Field('country', 'string', default='Unspecified', label='Country'),
                Field('subdivision', 'string', default='Unspecified', label='Sub-division'),
                Field('showcat', 'boolean', label='Show Category Filter', comment='Uncheck to show all'),
                Field('category', 'string', default='Unspecified', label='Category', comment='Optional'),
                Field('selection', 'string', default=['Issue', 'Question', 'Action', 'Resolved']),
                Field('execstatus', 'string', label='Execution Status',
                      default=['Proposed', 'Planned', 'In Progress', 'Completed']),
                Field('answer_group', 'string', default='Unspecified', label='Answer Group'),
                Field('searchstring', 'string', label='Search:', default=session.searchstring),
                Field('coord', 'string', label='Lat/Longitude'),
                Field('searchrange', 'integer', default=100, label='Search Range in Kilometers'),
                Field('startdate', 'date', default=request.utcnow, label='From Date'),
                Field('enddate', 'date', default=request.utcnow, label='To Date'),
                Field('linklevels', 'integer', default=1, label='No of generations of linked items',
                      requires=IS_IN_SET([0,1, 2, 3, 4, 5])))

# default = (session.coord or (auth.user and auth.user.coord))
db.viewscope.view_scope.requires = IS_IN_SET(scopes)
db.viewscope.sortorder.requires = IS_IN_SET(['1 Priority', '2 Resolved Date', '3 Submit Date', '4 Answer Date'])
db.viewscope.selection.requires = IS_IN_SET(['Issue', 'Question', 'Action', 'Proposed', 'Resolved', 'Draft'],
                                            multiple=True)
db.viewscope.selection.widget = hcheckbutton_widget
db.viewscope.execstatus.requires=IS_IN_SET(['Proposed', 'Planned', 'In Progress', 'Completed'], multiple=True)
db.viewscope.execstatus.widget = hcheckbutton_widget
db.viewscope.filters.requires = IS_IN_SET(['Scope', 'Category', 'AnswerGroup', 'Date', 'Project', 'Event'], multiple=True)
db.viewscope.filters.widget = hcheckbutton_widget

# db.viewscope.selection.widget = SQLFORM.widgets.checkboxes.widget
db.viewscope.view_scope.widget = hradio_widget
db.viewscope.sortorder.widget = hradio_widget
# db.viewscope.sortorder.widget = SQLFORM.widgets.radio.widget
db.viewscope.searchstring.requires = IS_NOT_EMPTY()

db.viewscope.coord.requires = IS_GEOLOCATION()
db.viewscope.coord.widget = location_widget()

PARAMS = db(db.website_parameters).select().first()