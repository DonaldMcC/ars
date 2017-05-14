from ndsfunctions import getitem

@auth.requires_login()
def index():
    # This allows creation of questions, actions and issues so the first
    # thing to do is establish whether question or action being submitted the
    # default is question unless action or issue specified and
    activityid = request.args(0, cast=int, default=0)
    record = 0

    if activityid:
        record = db.activity(activityid)
        if record.auth_userid != auth.user.id or record.status != 'Draft':
            session.flash = 'Not Authorised - items can only be edited by their owners when at draft status'
            redirect(URL('default', 'index'))

    db.activity.status.requires = IS_IN_SET(['Draft', 'Complete'])

    heading = 'Submit Activity'
    fields = ['activity', 'details', 'fullname', 'organisation', 'orgtype', 'activescope',
              'country', 'subdivision', 'town', 'coord', 'status', 'category']

    if activityid:
        form = SQLFORM(db.activity, record, fields=fields, deletable=True)
    else:
        form = SQLFORM(db.activity, fields=fields)

    form.element(_type='submit')['_class'] = "btn btn-success"

    if form.validate():
        form.vars.activity_lat, form.vars.activity_long = IS_GEOLOCATION.parse_geopoint(form.vars.coord)

        if activityid:
            form.vars.id = activityid
            if form.deleted:
                db(db.activity.id == activityid).delete()
                response.flash = 'Item deleted'
                redirect(URL('default', 'index'))
            else:
                record.update_record(**dict(form.vars))
                response.flash = 'Item updated'
                redirect(URL('default', 'index'))
        else:
            form.vars.id = db.activity.insert(**dict(form.vars))
        response.flash = 'form accepted'
        session.status = form.vars.status

        redirect(URL('accept_activity', args=[form.vars.id, form.vars.status]))
    elif form.errors:
        response.flash = 'form has errors'
    else:
        response.flash = 'please fill out the form'

    return dict(form=form, heading=heading)

def accept_activity():
    response.flash = "Details Submitted"
    activityid = request.args(0, default=0)
    status = request.args(1, default='InProg')
    item = getitem(activityid)
    activity = db(db.activity.id == activityid).select().first()

    return dict(status=status, item=item, activity=activity)

def subdivn():
    # This is called via Ajax to populate the subdivision dropdown on change of country
    # now changed to derelationalise country subdivision
    result = "<option value='Unspecified'>Unspecified</option>"
    print request.vars.country
    subdivns = db(db.subdivision.countryid == request.vars.country).select(
        db.subdivision.id, db.subdivision.subdiv_name, orderby=db.subdivision.subdiv_name,
        cache=(cache.ram, 1200), cacheable=True)
    for row in subdivns:
        if row.subdiv_name != request.vars.subdivision:
            result += "<option value='" + str(row.id) + "'>" + row.subdiv_name + "</option>"
        else:
            result += "<option value='" + str(row.id) + "' selected>" + row.subdiv_name + "</option>"

    return XML(result)

def country():
    result = "<option value='Unspecified'>Unspecified</option>"
    countries = db(db.country.id>0).select(
        db.country.country_name, cache=(cache.ram, 6000), cacheable=True)
    for countrie in countries:
        if countrie.country_name != request.vars.country:
            result += "<option value='" + str(countrie.country_name) + "'>" + countrie.country_name + "</option>"
        else:
            result += "<option value='" + str(countrie.country_name) + "' selected>" + countrie.country_name + "</option>"
    return XML(result)