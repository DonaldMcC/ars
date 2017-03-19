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
    fields = ['activity', 'details', 'forename', 'surname', 'organisation', 'orgtype', 'town',
                 'continent', 'country', 'subdivision', 'coord', 'status', 'category']

    if activityid:
        form = SQLFORM(db.activity, record, fields=fields, deletable=True)
    else:
        form = SQLFORM(db.activity, fields=fields)

    form.element(_type='submit')['_class'] = "btn btn-success"

    if form.validate():
        form.vars.activity_lat, form.vars.activity_long = IS_GEOLOCATION.parse_geopoint(form.vars.coord)

        if activityid:
            form.vars.id = questid
            if form.deleted:
                db(db.activity.id == activityid).delete()
                response.flash = 'Item deleted'
                redirect(URL('default', 'index'))
            else:
                record.update_record(**dict(form.vars))
                response.flash = 'Item updated'
                redirect(URL('default', 'index'))
        else:
            form.vars.id = db.question.insert(**dict(form.vars))
        response.flash = 'form accepted'
        session.status = form.vars.status

        redirect(URL('accept_activity', args=[form.vars.id, form.vars.status]))
    elif form.errors:
        response.flash = 'form has errors'
    else:
        response.flash = 'please fill out the form'

    return dict(form=form, heading=heading)