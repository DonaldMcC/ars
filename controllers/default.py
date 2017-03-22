# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

# -------------------------------------------------------------------------
# This is a sample controller
# - index is the default action of any application
# - user is required for authentication and authorization
# - download is for downloading files uploaded in the db (does streaming)
# -------------------------------------------------------------------------


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


