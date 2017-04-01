# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

# -------------------------------------------------------------------------
# This is a sample controller
# - index is the default action of any application
# - user is required for authentication and authorization
# - download is for downloading files uploaded in the db (does streaming)
# -------------------------------------------------------------------------
# from datetime import timedelta


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
    #   session.vwcontinent
    #   session.vwcountry
    #   session.vwsubdivision
    #   session.answer_group
    #   session.sortorder
    #   session.evtid
    #   session.projid
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

    strquery = (db.activity.status == 'Complete')

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


    if request.vars.sortby == 'rating':
        sortby = db.activity.rating
    else:
        sortby = ~db.activity.rating
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
