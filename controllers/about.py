# - Coding UTF8 -
#
# Activity Recording System
# Development Sites (source code): http://github.com/DonaldMcC/ars
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


# This controller provides details about network decision making
# access to the FAQ and allows generation of a general message
# on what we are looking to achieve
# The Press Release Note for the latest version is also now included
# and some basic capabilities to download actions have also been added

"""
    exposes:
    http://..../[app]/about/index
    http://..../[app]/about/privacy
    http://..../[app]/about/faq
    http://..../[app]/about/present
    http://..../[app]/about/enhance
    http://..../[app]/about/stdmsg
    http://..../[app]/about/download
    http://..../[app]/about/getfile

    """

session.forget(response)


def index():
    return dict(message="all done in the view")


def privacy():
    return dict(message="all done in the view")


def faq():
    return dict(message="all done in the view")


def present():
    return dict(message="all done in the view")


def enhance():
    return dict(message="all done in the view")


def download():
    downloads = db().select(db.download.ALL, orderby=db.download.title)
    return dict(downloads=downloads)


def getfile():
    return response.download(request, db)
