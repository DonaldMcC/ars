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

# This controller has x functions:
# newindex: the main review option
# newlist: this provides the views from the summary table on the home page
# activity: this is designed to show overview of what has been happening on the site between a range of dates
# my_answers - which should now be changed to use datatables

from datetime import timedelta


@auth.requires(True, requires_login=requires_login)
def newindex():
    # this provides an ajax version of review and 2 sections being draft and completed issues.
    # Users can only see their own draft issue

    # session variables will generally be used to preset values - but certain calls and views may use
    # an arg to override this

    # Plan is to have up to 5 arguments for this which I thnk will be
    # 1 View - v
    # 2 Query - q
    # 3 Sort Order - s
    # 4 Page
    # 5 Items Per Page

    # Valid values for view are:
    # draft,  completed, all - default will be completed
    # Valid values for query are:
    # reviewed, notreviewed, all and my - my is only valid if logged in
    # Valid values for sort order are
    # priority and  submitdate for now
    #
    # the query will be all the record filters and these will be managed with session variables

    heading = 'Resolved Questions'
    message = ''


    v = request.args(0, default='Complete')  # lets use this for my
    q = request.args(1, default='All')  # this matters
    s = request.args(2, default='Rating')  # this is the sort order

    fields = ['selection', 'sortorder', 'filters', 'view_scope', 'country', 'subdivision',
                  'category', 'startdate', 'enddate', 'coord', 'searchrange']

    page = request.args(3, cast=int, default=0)
    reset = request.args(4, default='No')  # This will reset just the selection

    if not session.selection or reset == 'Yes':
        session.selection = [v]
        session.query = q

    form = SQLFORM(db.viewscope, fields=fields, formstyle='table3cols',
                   buttons=[TAG.button('Submit', _type="submit", _class="btn btn-primary btn-group"),
                            TAG.button('Reset', _type="button", _class="btn btn-primary btn-group",
                            _onClick="parent.location='%s' " % URL('newindex', args=[v]))])
    
    numdays = 7  # default to 1 week

    if session.enddate:
        form.vars.enddate = session.enddate
    else:
        form.vars.enddate = request.utcnow.date() + timedelta(days=1)

    if session.startdate:
        form.vars.startdate = session.startdate
    else:
        form.vars.startdate = form.vars.enddate - timedelta(days=numdays)

    if session.category:
        form.vars.category = session.category
    else:
        form.vars.category = 'Unspecified'
    if session.view_scope:
        form.vars.view_scope = session.view_scope
    else:
        form.vars.view_scope = '1 Global'

    if session.vwcountry:
        form.vars.country = session.vwcountry
    else:
        form.vars.country = 1 #TODO this will change to default country at some point

    if session.vwsubdivision:
        form.vars.subdivision = session.vwsubdivision
    else:
        form.vars.subdivision = 1

    if session.coord:
        form.vars.coord = session.coord
    if session.searchrange:
        form.vars.searchrange = session.searchrange
    
    if session.filters:
        form.vars.filters = session.filters

    if session.sortorder:
        form.vars.sortorder = session.sortorder
    else:
        form.vars.sortorder = '1 Rating'
    if session.selection:
        form.vars.selection = session.selection
    else:
        form.vars.selection = 'Complete'

    items_per_page = 50
    limitby = (page * items_per_page, (page + 1) * items_per_page + 1)

    print 'sel', session.selection
    if form.validate():
    #   session.showcat
    #   session.showscope
        print session.selection
        session.view_scope = form.vars.view_scope
        session.category = form.vars.category
        session.vwcountry = form.vars.country
        session.vwsubdivision = form.vars.subdivision
        session.selection = form.vars.selection
        session.filters = form.vars.filters
        session.startdate = form.vars.startdate
        session.enddate = form.vars.enddate
        session.sortorder = form.vars.sortorder
        session.searchrange = form.vars.searchrange
        session.coord = form.vars.coord
        print 'valid'


        page = 0
        # redirect(URL('newindex', args=[v, q, s], vars=request.vars))
        # so thinking is that on initial call the args can over-ride the session variables

        redirect(URL('newindex', args=[v]))

    return dict(form=form, page=page, items_per_page=items_per_page, v=v, q=q,
                s=s, heading=heading, message=message)


@auth.requires(True, requires_login=requires_login)
def newlist():
    # this now uses load functionality - but more sorting out of answer_groups to be looked at once we have
    # better data
    message = 'test message'
    groupcat = request.args(0, default='C')
    groupcatname = request.args(1, default='Unspecified')
    qtype = request.args(2, default='quest')
    status = request.args(3, default='Resolved')
    items_per_page = 50

    if groupcat == 'C':
        category = groupcatname
        answer_group = 'Unspecified'
        group_filter = 'False'
        if category != 'Total':
            cat_filter = 'True'
        else:
            cat_filter = 'False'
    else:
        category = 'Unspecified'
        answer_group = groupcatname
        cat_filter = 'False'
        if answer_group != 'Total':
            group_filter = 'True'
        else:
            group_filter = 'False'

    selection = qtype[0].upper()
    if status == 'Resolved':
        selection += 'R'
    else:
        selection += 'P'

    if qtype == 'quest':
        qprint = 'Question'
    elif qtype == 'action':
        qprint = 'Action'
    else:
        qprint = 'Issue'
        
    if status == 'InProg':
        dispstatus = 'In Progress'
    else:
        dispstatus = status

    heading = 'Item:' + qprint + ' Filter:' + groupcatname + ' Status:' + status
    heading = dispstatus + ' ' + qprint + 's'
    if groupcatname != 'Total':
        heading += ' Filter:' + groupcatname

    return dict(category=category, answer_group=answer_group, qtype=qtype, status=status,
                selection=selection, heading=heading, message=message, cat_filter=cat_filter,
                group_filter=group_filter, items_per_page=items_per_page)


@auth.requires_login()
def activity():
    # This should support a report of activity in terms of both items submitted and actions resolved
    # thinking at present is not to use load and to not show too many details - perhaps
    # just the type and the question on submissions and the agreed answers and so on for quests
    # idea is that queries will be global and cacheable but will probably have to call a different
    # way eventually for email - it will also be callable via newindex and loaded in that case but will
    # NOT use session parameters instead these will be request vars to the extent supported

    period = request.args(0, default='weekly')
    format = request.args(1, default='html')
    source = request.args(2, default='default')
    view = request.args(3, default='All')  # will not use session variables as standard here so get everything#

    if view == 'resolved':
        response.view = 'review/resolved.load'
    elif view == 'submitted':
        response.view = 'review/submitted.load'
    # if run weekly or daily then lets run up to end of previous day - but final reports will
    # be dates

    if period == 'weekly':
        numdays = 7
    else:
        numdays = 1

    scope = request.vars.scope or (source != 'default' and session.view_scope) or '1 Global'
    category = request.vars.category or (source != 'default' and session.category) or 'Unspecified'
    vwcontinent = request.vars.vwcontinent or (source != 'default' and session.vwcontinent) or 'Unspecified'
    vwcountry = request.vars.vwcountry or (source != 'default' and session.vwcountry) or 'Unspecified'
    vwsubdivision = request.vars.vwsubdivision or (source != 'default' and session.vwsubdivision) or 'Unspecified'
    sortorder = request.vars.sortorder or (source != 'default' and session.sortorder) or 'Unspecified'
    event = request.vars.event or (source != 'default' and session.evtid) or 'Unspecified'
    project = request.vars.project or 'Unspecified'
    answer_group = request.vars.answer_group or (source != 'default' and session.answer_group) or 'Unspecified'
    startdate = request.vars.startdate or (source != 'default' and session.startdate) or (
                request.utcnow - timedelta(days=numdays))
    enddate = request.vars.enddate or (source != 'default' and session.enddate) or request.utcnow.date()    
    context = request.vars.context or 'Unspecified'
    enddate += timedelta(days=1)  # because reporting on a datetime field from date and defaults to 00:00:00

    filters = (source != 'default' and session.filters) or []
    # this can be Scope, Category, AnswerGroup and probably Event in due course

    scope_filter = request.vars.scope_filter or 'Scope' in filters
    cat_filter = request.vars.cat_filter or 'Category' in filters
    group_filter = request.vars.group_filter or 'AnswerGroup' in filters
    date_filter = request.vars.datefilter or 'Date' in filters
    event_filter = request.vars.event_filter or 'Event' in filters  # so this will now need to be included in some calls
    project_filter = request.vars.project_filter or 'Project' in filters

    if date_filter:
        crtquery = (db.question.createdate >= startdate) & (db.question.createdate <= enddate)
        resquery = (db.question.resolvedate >= startdate) & (db.question.resolvedate <= enddate)
        challquery = (db.question.challengedate >= startdate) & (db.question.challengedate <= enddate)
    else:
        crtquery = (db.question.id > 0)
        resquery = (db.question.id > 0)
        challquery = (db.question.id > 0)

    if cat_filter and cat_filter != 'False':
        crtquery &= (db.question.category == category)

    if scope_filter is True:
        crtquery &= db.question.activescope == scope
        if session.view_scope == '1 Global':
            crtquery &= db.question.activescope == scope
        elif session.view_scope == '2 Continental':
            crtquery &= (db.question.activescope == session.view_scope) & (db.question.continent == vwcontinent)
        elif session.view_scope == '3 National':
            crtquery &= (db.question.activescope == session.view_scope) & (db.question.country == vwcountry)
        elif session.view_scope == '4 Local':
            crtquery &= (db.question.activescope == session.view_scope) & (db.question.subdivision == vwsubdivision)

    if group_filter and group_filter != 'False':
        crtquery &= db.question.answer_group == answer_group

    if event_filter and event != 'Unspecified':
        crtquery &= db.question.eventid == event
        resquery &= db.question.eventid == event

    if project_filter and project != 'Unspecified':
        crtquery &= db.question.projid == project
        resquery &= db.question.projid == project

    orderstr = db.question.createdate
    resolvestr = db.question.resolvedate
    challstr = db.question.challengedate

    submitted = db(crtquery).select(orderby=orderstr)
    resolved = db(resquery).select(orderby=resolvestr)
    challenged = db(challquery).select(orderby=challstr)

    # remove excluded groups always
    if session.exclude_groups is None:
        session.exclude_groups = get_exclude_groups(auth.user_id)

    if session.exclue_groups:
        alreadyans = resolved.exclude(lambda r: r.answer_group in session.exclude_groups)
        alreadyans = submitted.exclude(lambda r: r.answer_group in session.exclude_groups)
        alreadyans = challenged.exclude(lambda r: r.answer_group in session.exclude_groups)

    return dict(submitted=submitted, resolved=resolved, challenged=challenged)


@auth.requires_login()
def my_answers():
    fields = ['sortorder', 'showscope', 'view_scope', 'continent', 'country', 'subdivision',
              'showcat', 'category']
    form = SQLFORM(db.viewscope, fields=fields, formstyle='table3cols')

    page = 0
    q = 'Que'
    s = 'Resolved'

    if session.showscope is None:
        form.vars.showscope = False
        form.vars.showcat = False
    else:
        form.vars.showscope = session.showscope
        form.vars.showcat = session.showcat
        form.vars.category = session.category
        form.vars.view_scope = session.view_scope
        form.vars.continent = session.vwcontinent
        form.vars.country = session.vwcountry
        form.vars.subdivision = session.vwsubdivision

    if session.sortorder is not None:
        form.vars.asortorder = session.sortorder

    if len(request.args):
        page = int(request.args[0])
        if len(request.args) > 1:
            q = request.args[1]
            if len(request.args) > 2:
                s = request.args[2]

    items_per_page = 50
    limitby = (page * items_per_page, (page + 1) * items_per_page + 1)

    if session.sortorder is not None:
        if session.sortorder == '1 Answer Date':
            s = 'Answer'
        elif session.sortorder == '2 Resolved Date':
            s = 'Resolved'
        elif session.sortorder == '3 Category':
            s = 'Category'

    if form.validate():
        session.showcat = form.vars.showcat
        session.showscope = form.vars.showscope
        session.view_scope = form.vars.view_scope
        session.category = form.vars.category

        session.vwcontinent = form.vars.continent
        session.vwcountry = form.vars.country
        session.vwsubdivision = form.vars.subdivision
        session.sortorder = form.vars.asortorder

        if session.sortorder == '1 Answer Date':
            s = 'Answer'
        elif session.sortorder == '2 Resolved Date':
            s = 'Resolved'
        elif session.sortorder == '3 Category':
            s = 'Category'

        page = 0
        redirect(URL('my_answers', args=[page, q, s]))

    # Actions can be selected for all or status of Agreed, In Progress or Disagreed
    # Rejected actions cannot be reviewed

    query = (db.userquestion.auth_userid == auth.user.id)
    if q == 'Resolved':
        query &= db.userquestion.status == 'Resolved'
    elif q == 'InProg':  # we are not showing this for philosophical reasons at the moment
        query &= db.userquestion.status == 'In Progress'

    if session.showcat is True:
        query &= (db.userquestion.category == session.category)
    if session.showscope is True:
        query &= (db.userquestion.activescope == session.view_scope)
        if session.view_scope == '1 Global':
            query &= db.userquestion.activescope == session.view_scope
        elif session.view_scope == '2 Continental':
            query = query & (db.userquestion.activescope == session.view_scope) & (
                db.userquestion.continent == session.vwcontinent)
        elif session.view_scope == '3 National':
            query = query & (db.userquestion.activescope == session.view_scope) & (
                db.userquestion.country == session.vwcountry)
        elif session.view_scope == '4 Provincial':
            query = query & (db.userquestion.activescope == session.view_scope) & (
                db.userquestion.subdivision == session.vwsubdivision)
        elif session.view_scope == '5 Local':
            # TO DO make this use geoquery
            query = query & (db.userquestion.activescope == session.view_scope) & (
                db.userquestion.subdivision == session.vwsubdivision)

    # And they can be sorted by create date, priority and due date    
    sortby = ~db.userquestion.ansdate

    if s == 'Resolved':
        sortby = ~db.userquestion.resolvedate
    elif s == 'Category':
        sortby = db.userquestion.category

    quests = db(query).select(orderby=[sortby], limitby=limitby)

    return dict(form=form, quests=quests, page=page, items_per_page=items_per_page, q=q, s=s, query=query)
