# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

# -------------------------------------------------------------------------
# This is a sample controller
# - index is the default action of any application
# - user is required for authentication and authorization
# - download is for downloading files uploaded in the db (does streaming)
# -------------------------------------------------------------------------
from datetime import timedelta
from geogfunctions import getbbox

def index():
    """
    This is the startup function.
    It retrieves the 5 highest priority actions, 5 most recently resolved quests
    and highest priority quests in progress.
    For actions - any status except rejected are wanted but to avoid an or or a
    not for GAE we will use ans3 for this purpose with numans always two for an
    action this is ok.  All queries are cached for 2 mins which should be OK
    """

    response.flash = "Welcome to ARS "
    activities = db(db.activity.id > 0).select()

    WEBSITE_PARAMETERS = db(db.website_parameters).select(cache=(cache.ram, 1200), cacheable=True).first()
    return dict(title=response.title, WEBSITE_PARAMETERS=WEBSITE_PARAMETERS, activities=activities)


@auth.requires(True, requires_login=requires_login)
def questload():
    # this got rather complicated - we will apply session variables if present otherwise  we will populate them
    # but sorting order and number of records, plus source and view will be args
    # possible session variables are:
    #   session.showcat
    #   session.showscope
    #   session.view_scope
    #   session.category
    #   session.vwcountry
    #   session.vwsubdivision
    #   session.sortorder
    #   session.searchrange
    #   session.coord
    # if source is default we don't care about session variables it's a standard view with request vars applied
    # but if other source then we should setup session variables and then apply request vars
    #   session.eventid is not used unless called from eventaddquests and the source will then need to be sent as
    # 'event' to get the button to add and remove from event as appropriate

    source = request.args(0, default='std')
    view = request.args(1, default='Action')
    scope = session.view_scope or None
    category = session.category or None
    q = request.vars.q or 'good'

    scope = request.vars.scope or (source != 'default' and session.view_scope) or '1 Global'
    category = request.vars.category or (source != 'default' and session.category) or 'Unspecified'
    vwcountry = request.vars.vwcountry or (source != 'default' and session.vwcountry) or 'Unspecified'
    vwsubdivision = request.vars.vwsubdivision or (source != 'default' and session.vwsubdivision) or 'Unspecified'
    sortorder = request.vars.sortorder or (source != 'default' and session.sortorder) or 'Unspecified'
    startdate = request.vars.startdate or (source != 'default' and session.startdate) or (
        request.utcnow - timedelta(days=1000))
    enddate = request.vars.enddate or (source != 'default' and session.enddate) or request.utcnow

    filters = (source != 'default' and session.filters) or []
    # this can be Scope, Category, AnswerGroup and probably Event in due course

    scope_filter = request.vars.scope_filter or 'Scope' in filters
    cat_filter = request.vars.cat_filter or 'Category' in filters
    date_filter = request.vars.datefilter or 'Date' in filters


    if q=='Draft':
        strquery = ((db.activity.status == 'Draft') & (db.activity.auth_userid == auth.user_id))
    else: # good, bad or complete
        strquery = (db.activity.status == 'Complete')

    if date_filter: #TODO make sure createdate gets updated when draft is completed
        strquery &= (db.activity.createdate >= startdate) & (db.activity.createdate <= enddate)

    if cat_filter and cat_filter != 'False':
        strquery &= (db.activity.category == category)

    if scope_filter is True:
        if session.view_scope == '1 National':
            strquery = strquery  & (db.activity.country == vwcountry)
        elif session.view_scope == '2 Regional':
            strquery = strquery & (db.activity.subdivision == vwsubdivision)
        elif session.view_scope == '3 Local':
            minlat, minlong, maxlat, maxlong = getbbox(session.coord, session.searchrange)
            strquery = strquery & ((current.db.activity.question_lat > minlat) &
                                  (current.db.activity.question_lat < maxlat) &
                                  (current.db.activity.question_long > minlong) &
                                  (current.db.activity.question_long < maxlong))

    if request.vars.page:
        page = int(request.vars.page)
    else:
        page = 0

    if request.vars.items_per_page:
        items_per_page = int(request.vars.items_per_page)
    else:
        items_per_page = 50

    limitby = (page * items_per_page, (page + 1) * items_per_page + 1)
    no_page = request.vars.no_page

    # TODO lets sort this later
    if request.vars.sortby == 'rating':
        sortby = db.activity.rating
    elif request.vars.sortby == 'revrating':
        sortby = ~db.activity.rating
    else:
        sortby = db.activity.createdate

    if debug:
        print(strquery)

    activity = db(strquery).select(orderby=[sortby], limitby=limitby)
    return dict(q=q, activity=activity, page=page, items_per_page=items_per_page, no_page=no_page)


@request.restful()
def api():

    def GET(*args, **vars):
        strquery = (db.activity.id > 0)
        quests = db(strquery).select(db.activity.details)
        return dict(quests=quests)

    def POST(*args, **vars):
        return dict()

    def PUT(*args, **vars):
        return dict()

    def DELETE(*args, **vars):
        return dict()

    return locals()


def user():
    """
    exposes:
    http://..../[app]/default/user/login
    http://..../[app]/default/user/logout
    http://..../[app]/default/user/register
    http://..../[app]/default/user/profile
    http://..../[app]/default/user/retrieve_password
    http://..../[app]/default/user/change_password
    http://..../[app]/default/user/bulk_register
    use @auth.requires_login()
        @auth.requires_membership('group name')
        @auth.requires_permission('read','table name',record_id)
    to decorate functions that need access control
    also notice there is http://..../[app]/appadmin/manage/auth to allow administrator to manage users
    """
    return dict(form=auth())


@cache.action()
def download():
    """
    allows downloading of uploaded files
    http://..../[app]/default/download/[filename]
    """
    return response.download(request, db)


def call():
    """
    exposes services. for example:
    http://..../[app]/default/call/jsonrpc
    decorate with @services.jsonrpc the functions to expose
    supports xml, json, xmlrpc, jsonrpc, amfrpc, rss, csv
    """
    return service()
