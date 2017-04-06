# -*- coding: utf-8 -*-

# -------------------------------------------------------------------------
# This scaffolding model makes your app work on Google App Engine too
# File is released under public domain and you can use without limitations
# -------------------------------------------------------------------------

# if request.global_settings.web2py_version < "2.14.1":
#    raise HTTP(500, "Requires web2py 2.13.3 or newer")

# -------------------------------------------------------------------------
# if SSL/HTTPS is properly configured and you want all HTTP requests to
# be redirected to HTTPS, uncomment the line below:
# -------------------------------------------------------------------------
# request.requires_https()

# -------------------------------------------------------------------------
# app configuration made easy. Look inside private/appconfig.ini
# -------------------------------------------------------------------------
from gluon.contrib.appconfig import AppConfig
from gluon.tools import Auth, Service, PluginManager
import os
from gluon.tools import Auth, PluginManager, prettydate, Mail
from gluon import *
from gluon.custom_import import track_changes
from plugin_location_picker import IS_GEOLOCATION, location_widget
not_empty = IS_NOT_EMPTY()


# once in production change to False
track_changes(True)

from gluon import current
from ndsfunctions import generate_thumbnail
# -------------------------------------------------------------------------
# once in production, remove reload=True to gain full speed
# -------------------------------------------------------------------------
myconf = AppConfig(reload=True)

if not request.env.web2py_runtime_gae:
    # ---------------------------------------------------------------------
    # if NOT running on Google App Engine use SQLite or other DB
    # ---------------------------------------------------------------------
    db = DAL(myconf.take('db.uri'),
             pool_size=myconf.take('db.pool_size', cast=int),
             migrate=myconf.take('db.migrate', cast=int),
             lazy_tables=myconf.take('db.lazy_tables', cast=int),
             check_reserved=['all'])
else:
    # ---------------------------------------------------------------------
    # connect to Google BigTable (optional 'google:datastore://namespace')
    # ---------------------------------------------------------------------
    db = DAL('google:datastore+ndb')
    # ---------------------------------------------------------------------
    # store sessions and tickets there
    # ---------------------------------------------------------------------
    session.connect(request, response, db=db)
    # ---------------------------------------------------------------------
    # or store session in Memcache, Redis, etc.
    # from gluon.contrib.memdb import MEMDB
    # from google.appengine.api.memcache import Client
    # session.connect(request, response, db = MEMDB(Client()))
    # ---------------------------------------------------------------------

# -------------------------------------------------------------------------
# by default give a view/generic.extension to all actions from localhost
# none otherwise. a pattern can be 'controller/function.extension'
# -------------------------------------------------------------------------
response.generic_patterns = ['*'] if request.is_local else []
# -------------------------------------------------------------------------
# choose a style for forms
# -------------------------------------------------------------------------
response.formstyle = myconf.get('forms.formstyle')  # or 'bootstrap3_stacked' or 'bootstrap2' or other
response.form_label_separator = myconf.get('forms.separator') or ''

# -------------------------------------------------------------------------
# (optional) optimize handling of static files
# -------------------------------------------------------------------------
# response.optimize_css = 'concat,minify,inline'
# response.optimize_js = 'concat,minify,inline'

# -------------------------------------------------------------------------
# (optional) static assets folder versioning
# -------------------------------------------------------------------------
# response.static_version = '0.0.0'

# -------------------------------------------------------------------------
# Here is sample code if you need for
# - email capabilities
# - authentication (registration, login, logout, ... )
# - authorization (role based authorization)
# - services (xml, csv, json, xmlrpc, jsonrpc, amf, rss)
# - old style crud actions
# (more options discussed in gluon/tools.py)
# -------------------------------------------------------------------------

login = myconf.take('login.logon_methods')

if login == 'socialauth':
    from plugin_social_auth.utils import SocialAuth
    auth = SocialAuth(db)
    username_field = True  # This is required
else:
    auth = Auth(db, hmac_key=Auth.get_or_create_key())
    username_field = False  # can set to true if you want login by username rather than email

# host names must be a list of allowed host names (glob syntax allowed)
# auth = Auth(db, host_names=myconf.get('host.names'))
service = Service()
plugins = PluginManager()

# -------------------------------------------------------------------------
# create all tables needed by auth if not custom tables
# -------------------------------------------------------------------------
#auth.define_tables(username=False, signature=False)

# -------------------------------------------------------------------------
# configure email
# -------------------------------------------------------------------------
mail = auth.settings.mailer
#mail.settings.server = 'logging' if request.is_local else myconf.get('smtp.server')
#mail.settings.sender = myconf.get('smtp.sender')
#mail.settings.login = myconf.get('smtp.login')
mail.settings.tls = myconf.get('smtp.tls') or False
mail.settings.ssl = myconf.get('smtp.ssl') or False



mail.settings.server = myconf.take('smtp.server')
mail.settings.sender = myconf.take('smtp.sender')
mail.settings.login = myconf.take('smtp.login')


debug = myconf.take('developer.debug', cast=int)
if debug:
    mail.settings.server = 'logging:emailout.html'

# -------------------------------------------------------------------------
# configure other settings
# -------------------------------------------------------------------------

backend = myconf.take('search.backend')
response.formstyle = myconf.take('forms.formstyle')  # or 'bootstrap3_stacked'
response.form_label_separator = myconf.take('forms.separator')
requires_login = myconf.take('site.require_login', cast=int)
dbtype = myconf.take('db.dbtype')
hostadds = myconf.take('google.hostadds', cast=int)
ad_client = myconf.take('google.ad_client')
ad_slot = myconf.take('google.ad_slot', cast=int)
init = myconf.take('init.initialised', cast=int)


db.define_table('category',
                Field('cat_desc', 'string', label='Category',
                      requires=[not_empty, IS_NOT_IN_DB(db, 'category.cat_desc'), IS_LOWER()]),
                Field('categorydesc', 'text', label='Description'),
                format='%(cat_desc)s')

db.define_table('country',
                Field('country_name', 'string', label='Country',
                      requires=[not_empty, IS_SLUG(), IS_NOT_IN_DB(db, 'country.country_name')]),
                Field('continent', 'string', label='Continent'),
                format='%(country_name)s')

db.define_table('subdivision',
                Field('subdiv_name', 'string', label='Sub-division'),
                Field('country', 'string'),
                format='%(subdiv_name)s')

userfields = [
    Field('numratings', 'integer', default=0, readable=False, writable=False, label='Answered'),
    Field('exclude_categories', 'list:reference category', label='Excluded Categories',
          comment="Select categories you DON'T want to see"),
    Field('country', 'reference country', default='Unspecified', label='Country'),
    Field('subdivision', 'reference subdivision', default='Unspecified', label='Sub-division'),
    Field('town', 'string', default='Unspecified', label='Town'),
    Field('avatar', 'upload'),
    Field('avatar_thumb', 'upload', compute=lambda r: generate_thumbnail(r['avatar'], 120, 120, True)),
    Field('show_help', 'boolean', default=True, label='Show help')]



userfields.append(Field('coord', 'string', label='Lat/Longitude'))
userfields.append(Field('localrange', 'integer', default= 100, label='Radius for local issues',
                        comment='In Kilometers',requires=IS_INT_IN_RANGE(1, 1000,
                        error_message='Must be between 1 and 1000')))



auth.settings.extra_fields['auth_user'] = userfields

# create all tables needed by auth if not custom tables
auth.define_tables(username=username_field)
auth.settings.auth_manager_role = 'manager'
auth.settings.username_case_sensitive = False
auth.settings.email_case_sensitive = False


#db.auth_user.coord.requires = IS_GEOLOCATION()
#db.auth_user.coord.widget = location_widget()
# , widget=range_widget #TODO see if this can be scalable

# -------------------------------------------------------------------------
# configure auth policy
# -------------------------------------------------------------------------
auth.settings.registration_requires_verification = False
auth.settings.registration_requires_approval = False
auth.settings.reset_password_requires_verification = True

# -------------------------------------------------------------------------
# Define your tables below (or better in another model file) for example
#
# >>> db.define_table('mytable', Field('myfield', 'string'))
#
# Fields can be 'string','text','password','integer','double','boolean'
#       'date','time','datetime','blob','upload', 'reference TABLENAME'
# There is an implicit 'id integer autoincrement' field
# Consult manual for more options, validators, etc.
#
# More API examples for controllers:
#
# >>> db.mytable.insert(myfield='value')
# >>> rows = db(db.mytable.myfield == 'value').select(db.mytable.ALL)
# >>> for row in rows: print row.id, row.myfield
# -------------------------------------------------------------------------

# -------------------------------------------------------------------------
# after defining tables, uncomment below to enable auditing
# -------------------------------------------------------------------------
# auth.enable_record_versioning(db)
