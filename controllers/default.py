# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

# -------------------------------------------------------------------------
# This is a sample controller
# - index is the default action of any application
# - user is required for authentication and authorization
# - download is for downloading files uploaded in the db (does streaming)
# -------------------------------------------------------------------------
from datetime import timedelta

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
    #if not init:
    #    redirect(URL('admin', 'init'))

    activities = db(db.activity.id>0).select()

    WEBSITE_PARAMETERS = db(db.website_parameters).select(cache=(cache.ram, 1200), cacheable=True).first()
    return dict(title=response.title, WEBSITE_PARAMETERS=WEBSITE_PARAMETERS, activities=activities)


@auth.requires(True, requires_login=requires_login)
def questload():
    # latest thinking is thar request variables would apply if present but otherwise
    # may want to use session variables - but not on home page so maybe have some request args
    # as well - so lets try default to not apply session variables and then qtype for action/issue for now
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

    # sort of got idea of v, q and s to consider for view, strquery and sort order

    scope = request.vars.scope or (source != 'default' and session.view_scope) or '1 Global'
    category = request.vars.category or (source != 'default' and session.category) or 'Unspecified'
    vwcontinent = request.vars.vwcontinent or (source != 'default' and session.vwcontinent) or 'Unspecified'
    vwcountry = request.vars.vwcountry or (source != 'default' and session.vwcountry) or 'Unspecified'
    vwsubdivision = request.vars.vwsubdivision or (source != 'default' and session.vwsubdivision) or 'Unspecified'
    sortorder = request.vars.sortorder or (source != 'default' and session.sortorder) or 'Unspecified'
    event = request.vars.event or (source != 'default' and session.evtid) or 0
    project = request.vars.project or (source != 'default' and session.projid) or 'Unspecified'

    answer_group = request.vars.answer_group or (source != 'default' and session.answer_group) or 'Unspecified'
    startdate = request.vars.startdate or (source != 'default' and session.startdate) or (
        request.utcnow - timedelta(days=1000))
    enddate = request.vars.enddate or (source != 'default' and session.enddate) or request.utcnow

    filters = (source != 'default' and session.filters) or []
    # this can be Scope, Category, AnswerGroup and probably Event in due course

    scope_filter = request.vars.scope_filter or 'Scope' in filters
    cat_filter = request.vars.cat_filter or 'Category' in filters
    group_filter = request.vars.group_filter or 'AnswerGroup' in filters
    date_filter = request.vars.datefilter or 'Date' in filters
    event_filter = request.vars.event_filter or 'Event' in filters  # so this will now need to be included in some calls
    project_filter = request.vars.project_filter or 'Project' in filters

    selection = (source not in ('default', 'event', 'evtunlink', 'projlink', 'projunlink') and session.selection) or [
        'Question', 'Resolved']

    # selection will currently be displayed separately
    # db.viewscope.selection.requires = IS_IN_SET(['Issue','Question','Action','Proposed','Resolved','Draft'
    # so possibly maybe IP, IR, IM, QP, QR, QM, AP, AR, AM - but this can maybe always be in the URL

#top 5 and bottom 5 only?
    strquery = (db.activity.status == 'Complete')
    
    if date_filter:
        strquery &= (db.activity.createdate >= startdate) & (db.activity.createdate <= enddate)

    if cat_filter and cat_filter != 'False':
        strquery &= (db.activity.category == category)

    if scope_filter is True:
        strquery &= db.activity.activescope == scope
        if session.view_scope == '1 Global':
            strquery &= db.activity.activescope == scope
        elif session.view_scope == '2 Continental':
            strquery = strquery & (db.activity.activescope == session.view_scope) & (
                db.activity.continent == vwcontinent)
        elif session.view_scope == '3 National':
            strquery = strquery & (db.activity.activescope == session.view_scope) & (
                db.activity.country == vwcountry)
        elif session.view_scope == '4 Provincial':
            strquery = strquery & (db.activity.activescope == session.view_scope) & (
                db.activity.subdivision == vwsubdivision)
        elif session.view_scope == '5 Local':
            minlat, minlong, maxlat, maxlong = getbbox(session.coord, session.searchrange)
            strquery = strquery & (db.activity.activescope == session.view_scope) & (
                (current.db.activity.question_lat > minlat) &
                (current.db.activity.question_lat < maxlat) &
                (current.db.activity.question_long > minlong) &
                (current.db.activity.question_long < maxlong))

    if request.vars.sortby == 'ResDate':
        sortorder = '2 Resolved Date'
    elif request.vars.sortby == 'Priority':
        sortorder = '1 Priority'
    elif request.vars.sortby == 'CreateDate':
        sortorder = '3 Submit Date'


    sortby = ~db.activity.createdate

    if request.vars.page:
        page = int(request.vars.page)
    else:
        page = 0

    if request.vars.items_per_page:
        items_per_page = int(request.vars.items_per_page)
    else:
        items_per_page = 50

    limitby = (page * items_per_page, (page + 1) * items_per_page + 1)
    q = request.vars.selection

    no_page = request.vars.no_page

    # removed caching for now as there are issues
    # quests = db(strquery).select(orderby=[sortby], limitby=limitby, cache=(cache.ram, 1200), cacheable=True)
    quests = db(strquery).select(orderby=[sortby], limitby=limitby)

    # remove excluded groups always

    return dict(strquery=strquery, quests=quests, page=page, source=source, items_per_page=items_per_page, q=q,
                view=view, no_page=no_page, event=event)


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


