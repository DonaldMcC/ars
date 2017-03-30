# - Coding UTF8 -
#
# Networked Decision Making
# Development Sites (source code): http://github.com/DonaldMcC/gdms
#
# Demo Sites (Pythonanywhere)
#   http://netdecisionmaking.com/ars/
#   http://netdecisionmaking.com/arsdemo/
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


# The first user to register gets given admin privileges


"""
    exposes:
    This needs fully updated but do at the end
    http://..../[app]/admin/checkquestcounts
    http://..../[app]/about/index change
    http://..../[app]/about/privacy update
    http://..../[app]/about/faq update
    http://..../[app]/about/pr update
    http://..../[app]/about/enhance remove
    http://..../[app]/about/stdmsg change in database
    http://..../[app]/about/download keep
    http://..../[app]/about/get works with download

    """


from arsfunctions import email_setup, getindex

@auth.requires_membership('manager')
def emailtest():
    # This option is not on the main menu - may add another menu with checks and dashboard
    subject = 'Test Email'
    msg = 'This is a test message'
    params = current.db(current.db.website_parameters.id > 0).select().first()
    if params:
        stripheader = params.website_url[7:]
    else:
        stripheader = 'website_url_not_setup'
    if login == 'socialauth':
        controller = 'user'
        itemurl = URL('plugin_social_auth', controller, args=['profile'], scheme='http', host=stripheader)
    else:
        controller = 'user'
        itemurl = URL('default', controller, args=['profile'], scheme='http', host=stripheader)
    footer = 'You can manage your email preferences at ' + itemurl
    msg += footer
    result = send_email(mail.settings.sender, mail.settings.sender, subject, msg)
    if result is True:
        message = 'email sent'
    else:
        message = 'there was an error sending email'

    return message


@auth.requires_membership('manager')
def checkquestcounts():
    """ This will iterate through questions and count the numbers
        at each status to verify that the questcounts table is in line with the
        status of the questions we should build a dictionary of dictionaroes in general keyed on
        the id of the matching questcount record as that should make updating - if no matching
        questcount then key will be insert1, 2, 3 etc """

    groupcat = request.args(0, default='G')
    fix = request.args(1, default='no')
    if groupcat not in {'C', 'G'}:
        dict(message='First argument must be C or G', errors=None, errorlist=None, fix=fix, groupcat=groupcat)
    quests = db(db.question.id > 0).select()
    questcountdict = {}

    for quest in quests:
        if groupcat == 'G':
            groupcatname = quest.answer_group
        else:
            groupcatname = quest.category

        grouprow = db((db.questcount.groupcatname == groupcatname) & (db.questcount.groupcat == groupcat)
                      ).select().first()

        countindex = getindex(quest.qtype, quest.status)
        if grouprow is None or not (grouprow.id in questcountdict):
            # create a new key based on index
            createcount = [0] * 18
            createcount[countindex] = 1
            # need to actually look for key in dictionary as well here I think
            if grouprow is None:
                key = 99999999
            else:
                key = grouprow.id
            questcountdict[key] = {'groupcat': groupcat,
                                   'groupcatname': groupcatname, 'questcounts': createcount, 'id': key}
        else:
            questcountdict[grouprow.id]['questcounts'][countindex] += 1

    errors = False
    errorlist = []
    for key in questcountdict:
        grouprow = db(db.questcount.id == key).select().first()
        if not grouprow:
            errors = True
            errorlist.append(['missing', questcountdict])
            if fix == 'yes':
                questcountdict[key].pop('id', None)  # don't create missing record with key 9999999
                db.questcount.insert(**questcountdict[key])
        else:
            # existrow = existrows.first()
            if grouprow.questcounts != questcountdict[key]['questcounts']:
                errors = True
                errorlist.append([grouprow, questcountdict[key]])
                if fix == 'yes':
                    db(db.questcount.id == key).update(**questcountdict[key])

    if errors:
        if groupcat == 'G':
            message = 'Question counts for groups are incorrect'
        else:
            message = 'Question counts for categories are incorrect'
    else:
        if groupcat == 'G':
            message = 'All question counts for groups agree'
        else:
            message = 'All question counts for categories agree'

    return dict(message=message, errors=errors, errorlist=errorlist, fix=fix, groupcat=groupcat)


@auth.requires_membership('manager')
def index():
    return locals()

# This allows editing of the website_parameters of the decision making system
@auth.requires_membership('manager')
def website_parameters():
    grid = SQLFORM.grid(db.website_parameters)
    return dict(grid=grid)


# This allows editing of the categories within the subject of the system
@auth.requires_membership('manager')
def category():
    grid = SQLFORM.grid(db.category)
    return dict(grid=grid)


@auth.requires_membership('manager')
def mgr_activity():
    grid = SQLFORM.grid(db.activity, ignore_rw=True,
                        formstyle=SQLFORM.formstyles.bootstrap3_inline)
    return locals()


@auth.requires_membership('manager')
def mgr_answers():
    grid = SQLFORM.grid(db.useractivity, ignore_rw=True, orderby=[~db.activity.createdate])
    return locals()


@auth.requires_membership('manager')
def mgr_users():
    grid = SQLFORM.grid(db.auth_user, ignore_rw=True, orderby=[~db.auth_user.id])
    return locals()


@auth.requires_membership('manager')
def continent():
    grid = SQLFORM.grid(db.continent)
    return dict(grid=grid)


@auth.requires_membership('manager')
def country():
    grid = SQLFORM.grid(db.country)
    return dict(grid=grid)


@auth.requires_membership('manager')
def subdivision():
    grid = SQLFORM.grid(db.subdivision)
    return dict(grid=grid)


@auth.requires_membership('manager')
def messages():
    grid = SQLFORM.grid(db.app_message)
    return dict(grid=grid)


@auth.requires_membership('manager')
def company():
    grid = SQLFORM.grid(db.company)
    return dict(grid=grid)


@auth.requires_membership('manager')
def individual():
    grid = SQLFORM.grid(db.individual)
    return dict(grid=grid)


@auth.requires_membership('manager')
def event():
    grid = SQLFORM.grid(db.evt)
    return dict(grid=grid)


@auth.requires_membership('manager')
def access_group():
    grid = SQLFORM.grid(db.access_group)
    return dict(grid=grid)


@auth.requires_membership('manager')
def group_members():
    grid = SQLFORM.grid(db.group_members)
    return dict(grid=grid)


@auth.requires_membership('manager')
def eventmap():
    grid = SQLFORM.grid(db.eventmap)
    return dict(grid=grid)


@auth.requires_membership('manager')
def location():
    grid = SQLFORM.grid(db.locn)
    return dict(grid=grid)


@auth.requires_membership('manager')
def upload():
    grid = SQLFORM.grid(db.download)
    return dict(grid=grid)


@auth.requires_membership('manager')
def resolvemethod():
    grid = SQLFORM.grid(db.resolve)
    return dict(grid=grid)


# This allows editing of the categories within the subject of the system
@auth.requires_membership('manager')
def email_runs():
    grid = SQLFORM.grid(db.email_runs)
    return dict(grid=grid)


@auth.requires_membership('manager')
def approveusers():
    users = db(db.auth_user.registration_key == 'pending').select(db.auth_user.id,
                                                                  db.auth_user.first_name, db.auth_user.last_name,
                                                                  db.auth_user.email,
                                                                  db.auth_user.registration_key)

    return dict(users=users)


@auth.requires_membership('manager')
def clearactivity():
    db.eventmap.drop()
    db.userquestion.drop()
    db.questagreement.drop()
    db.questchallenge.drop()
    db.questcomment.drop()
    db.questcount.drop()
    db.questlink.drop()
    db.questurgency.drop()
    db.question.truncate()
    db.actiongroup.truncate()
    db(db.evt.evt_name != 'Unspecified').delete()
    return dict(message='All quests cleared')


@auth.requires_membership('manager')
def clearall():
    db.useractivity.drop()
    db.activity.drop()
    db.website_parameters.drop()

    return dict(message='Entire Database excecpt auth cleared out')


@auth.requires_membership('manager')
def fullreset():
    for table_name in db.tables():
        db[table_name].drop()

    return dict(message='Everything cleared out')


@auth.requires_login()
def datasetup():
    # This now needs reworked as some of the data needs to be creaed prior to the models execution
    # and so tables won't be empty - I think approach is to add all missing data which is slow
    # but effective will pull everything and then add the missing ones

    mgr = db(db.auth_group.role == 'manager').select().first()
    if mgr is None:
        mgr = auth.add_group('manager', 'The admin group for the app')
        auth.add_membership(mgr, auth.user_id)

    if db(db.category.id > 0).isempty():
        db.category.insert(cat_desc="None",
                           categorydesc="Set to select all questions")
        db.category.insert(cat_desc="Unspecified",
                           categorydesc="Catchall category")

    if db(db.website_parameters.id > 0).isempty():
        db.website_parameters.insert(website_name='ARS Test System', website_title='Activity Recording System',
                                     website_url='http://127.0.0.1:8081',
                                     longdesc='This is a test version of activity recording',
                                     shortdesc='Test net decision making',
                                     level1desc='Contnent', level2desc='Countrie', level3desc='Area',
                                     seo_meta_author='Russ King',
                                     seo_meta_description='Platform for recording activity')

    if db(db.system_scope.description == "1 Global").isempty():
        db.system_scope.insert(description="1 Global")
    if db(db.system_scope.description == "2 Continental").isempty():
        db.system_scope.insert(description="2 Continental")
    if db(db.system_scope.description == "3 National").isempty():
        db.system_scope.insert(description="3 National")
    if db(db.system_scope.description == "4 Local").isempty():
        db.system_scope.insert(description="4 Local")

    if db(db.continent.continent_name == "Unspecified").isempty():
        db.continent.insert(continent_name="Unspecified")

    if db(db.country.country_name == "Unspecified").isempty():
        db.country.insert(country_name="Unspecified", continent="Unspecified")

    # email_setup()
    # schedule_email_runs()

    return locals()


@auth.requires_login()
def init():
    # This function will be called to initialise the system the following
    # activities are required here
    # 1  Give the intial user manager role to admin the system
    # 2  Populate the scoring table
    # 3  Key in the subject of the database
    # 4  Provide details of how to admin the system
    # 5  Add a default category

    login = myconf.take('login.logon_methods')
    if db(db.website_parameters.id > 0).isempty():
        google_analytics_id = myconf.take('google.analytics_id')
        db.website_parameters.insert(shortdesc="This system should be used for any topic",
                                     longdesc='This system should be used for questions on any topic that '
                                              'you consider important to human progress',
                                     google_analytics_id=google_analytics_id)

    # Need to also ensure unspecified continent,region and country are present
    # think values will now be mandatory for new user registration

    # Update the first user to have manager access
    # Add an auth_group record of manager if it doesn't exist

    mgr = db(db.auth_group.role == 'manager').select().first()
    if mgr is None:
        mgr = auth.add_group('manager', 'The admin group for the app')
        auth.add_membership(mgr, auth.user_id)
    return locals()


@auth.requires_membership('manager')
def addstdcategories():
    categories = [["Unspecified", "Catchall category"],
                  ["Water", "Clean Water and Sanitation"],
                  ["No Poverty", "No Poverty"], ["Gender Equality", "Gender Equality"],
                  ["Food", "Zero Hunger"],  ["Energy", "Affordable and Clean Energy"],
                  ["Healthcare", "Good Health and Well-being"], ["Industry", "Industry, Innovation and Infrastructure"],
                  ["Reduced Inequalities", "Reduced Inequalities"],  ["Education", "Quality Education"],
                  ["Work", "Decent Work and Economic Growth"]]

    for x in categories:
        if db(db.category.cat_desc == x[0]).isempty():
            db.category.insert(cat_desc=x[0], categorydesc=x[1])

    return locals()


@auth.requires_membership('manager')
def ajaxapprove():
    # This allows managers to approve pending registrations
    userid = request.args[0]
    upd = ''
    responsetext = 'User ' + str(userid) + ' has been approved'
    messagetxt = 'Your registration request has been approved'
    link = URL('default', 'index', scheme=True, host=True)
    footnote = 'You can now access the site at: ' + link
    if len(request.args) > 1:
        upd = 'denied'
        responsetext = 'User ' + str(userid) + ' has been denied access for now'
        messagetxt = 'Your registration request has been denied'
        footnote = 'A specific email will be sent to explain why or request more information'

    db(db.auth_user.id == userid).update(registration_key=upd)

    email = db(db.auth_user.id == userid).select(
        db.auth_user.email).first().email

    messagetxt = messagetxt + '\n' + footnote
    mail.send(to=email,
              subject='Networked Decision Making Registration Request',
              message=messagetxt)

    return responsetext


@auth.requires_membership('manager')
def import_files():
    form = FORM(INPUT(_type='file', _name='data'), INPUT(_type='submit'))
    if form.process().accepted:
        db.import_from_csv_file(form.vars.data.file, unique=False)
    return locals()
