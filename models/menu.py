# -*- coding: utf-8 -*-
# - Coding UTF8 -
#
# Networked Decision Making
# Development Sites (source code): http://github.com/DonaldMcC/gdms
#
# Demo Sites (Pythonanywhere)
#   http://netdecisionmaking.com/nds/
#   http://netdecisionmaking.com/gdmsdemo/
#
# License Code: MIT
# License Content: Creative Commons Attribution 3.0
#
# Also visit: www.web2py.com
# or Groups: http://groups.google.com/group/web2py
# For details on the web framework used for this development
#
# With thanks to Guido, Massimo and many other that make this sort of thing
# much easier than it used to be

# ########################################################################
# Customize your APP title, subtitle and menus here
# #######################################################################
response.title = request.application.replace('_', ' ').title()
# response.title = ' '.join(word.capitalize() for word in request.application.split('_'))
# response.subtitle = T('A whole new paradigm for decision making')

# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

# #######################################################################
#  Customize your APP title, subtitle and menus here
# #######################################################################


response.logo = IMG(_src=URL('static', 'images/ndslogo.svg'), _class="img-thumbnail img-responsive visible-lg-inline",
                    _alt="NDS Logo")

# read more at http://dev.w3.org/html5/markup/meta.name.html
response.meta.author = 'Russ King <newglobalstrategy@gmail.com>'
response.meta.description = 'Network Decision Making'
response.meta.keywords = 'web2py, python, framework, global, decision-making'
response.meta.generator = 'Web2py Web Framework, Networked Decision Making'
response.meta.copyright = 'Has been phased out on more advanced planets'

# your http://google.com/analytics id
response.google_analytics_id = None

# #######################################################################
# # this is the main application menu add/remove items as required
# #######################################################################
#  [('Search', False, URL('search', 'index'))]),


response.menu = [
    ('About', False, '#',
     [('Home', False, URL('default', 'index')),
      ('Search', False, URL('search', 'newsearch')),
      ('About ARS', False, URL('about', 'index')),
      ('FAQ', False, URL('about', 'faq')),
      ('Enhancements', False, URL('about', 'enhance')),
      ('Privacy Policy', False, URL('about', 'privacy')),
      ('Downloads', False, URL('about', 'download'))]),
      ('Create', False, URL('submit', 'index')),
      ('Review', False, URL('review', 'newindex')),
      ('My ARS', False, '#',
     [('My Reports', False, URL('review', 'newindex', args=['Complete', 'my'])),
      ('My Draft Reports', False, URL('review', 'newindex', args=['Draft', 'my'])),
      ('My Reviews', False, URL('review', 'my_ratings'))])
]


if auth.has_membership('manager'): 
    response.menu += [
        (T('Admin'), False, '#', [(T('Admin'), False, URL('admin', 'index')),
                                  (T('Upgrade'), False, URL('upgrade', 'index')),
                                  ('Appadmin', False, URL('appadmin', 'manage', args=['auth']))])]
