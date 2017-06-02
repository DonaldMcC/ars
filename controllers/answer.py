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

from ndsfunctions import score_question

"""
This controller handles the selection of an available question and the 
answering of it
6 Mar 2013 - rewrite to improve logic and consider 'late' answers to questions
which might be quite common as operation of selection is to always give the
highest priority question out to all users and work on resolving it first

    exposes:
    http://..../[app]/answer/all_questiona - basically still the same
    http://..../[app]/answer/get_question -- stays
    http://..../[app]/about/answer_question - enhance
    http://..../[app]/answer/quickanswer - ajax submission of answers to issues and actions
    http://..../[app]/answer/score_complete_votes - enquiry for scoring overdue votes 
    should be 4 views from this controller but get_question never called and no score complete votes yet
    
"""

# TODO add reject handling to submit
from arsfunctions import update_ratings

# @auth.requires_signature()


@auth.requires_login()
def answer_question():
    """
    This allows the user to answer the question or pass and the result is 
    handled by the score question function.  This can really now be called
    from any event and it is an exposed url - so now need to check if not 
    resolved or already answered and if so we will not accept another answer
    """

    activityid = request.args(0, cast=int, default=0)
    activity = db.activity[activityid]
    old_rating = 0
    old_impact = 0

    ur = db((db.user_rating.activityid == activityid) & (db.user_rating.auth_userid == auth.user_id)).select().first()
    if ur:
        form2 = SQLFORM(db.user_rating, ur.id,  showid=False, fields=['rating', 'impact', 'reject'],
                    submit_button='Submit', col3={'reject': 'Select if invalid or off subject '},
                                                  formstyle='table3cols')
        old_rating = ur.rating
        old_impact = ur.impact
    else:
        form2 = SQLFORM(db.user_rating, showid=False, fields=['rating', 'impact', 'reject'],
                    submit_button='Submit', col3={'reject': 'Select if invalid or off subject '},
                                                  formstyle='table3cols')

    form2.element(_type='submit')['_class'] = "btn btn-success"

    if ur:  # already rated so will need to populate form vars with current values
        form2.vars.rating = ratings[int(ur['rating'])-1]
        form2.vars.impact = int(ur['impact'])

    if form2.validate():
        form2.vars.auth_userid = auth.user.id
        form2.vars.activityid = activityid
        form2.vars.rating = form2.vars.rating[0]
        form2.vars.impact = form2.vars.impact[0]  # TODO check this works with 10 ratings 2 chars
        new_numratings = activity.numratings
        if form2.deleted:
            db(db.user_rating.id == activityid).delete()
            response.flash = 'Rating deleted'
            action = 'delete'
            new_numratings -= 1
        elif ur:
            ur.update_record(**dict(form2.vars))
            action = 'update'
            response.flash = 'Rating updated'
        else:
            form2.vars.id = db.user_rating.insert(**dict(form2.vars))
            action='create'
            new_numratings += 1
            response.flash = 'form accepted'
        new_rating = update_ratings(activity.rating, int(form2.vars.rating[0]), activity.numratings, old_rating, action)
        new_impact = update_ratings(activity.impact, int(form2.vars.impact[0]) , activity.numratings, old_impact, action)

        activity.update_record(rating=new_rating, impact=new_impact, numratings=new_numratings)
        redirect(URL('viewquest', 'index', args=[activityid]))
    elif form2.errors:
        response.flash = 'form has errors'
    return dict(form2=form2, activity=activity)


@auth.requires_login()
def quickanswer():
    """
    This will be left as may be persuaded to allow quick rating of activity - however current thinking is
    that users should not be rating activity they have not looked at in some detail
    """

    activityid = request.args(0, cast=int, default=0)
    rating = request.args(1, cast=int, default=-1)

    activity = db(db.activity.id == activityid).select().first()
    ur = db((db.user_rating.activityid == activityid) & (db.user_rating.auth_userid == auth.user_id)).select()

    if activity and not ur:
        uqid = db.userquestion.insert(questionid=questid, auth_userid=auth.user_id, uq_level=quest.question_level,
                                      answer=answer, reject=False, urgency=quest.urgency, importance=quest.importance,
                                      category=quest.category, activescope=quest.activescope, continent=quest.continent,
                                      country=quest.country)

        status = score_question(questid, uqid)
        if status == 'Resolved':
            scheduler.queue_task('send_email_resolved', pvars=dict(questid=questid), period=600)
        messagetxt = 'Answer recorded for item:' + str(questid)

        intunpanswers = quest.unpanswers
        if answer != -1:
            intunpanswers += 1

        if session.answered:  # optional if user selects question to answer
            session.answered.append(questid)
        anscount = quest.answercounts
        anscount[answer] += 1

        # update the question record based on above
        db(db.question.id == quest.id).update(answercounts=anscount, unpanswers=intunpanswers,
                                              urgency=quest.urgency, importance=quest.importance)
    elif uq:
        messagetxt = 'You have already answered this item'
    else:
        messagetxt = 'Answer not recorded'

    return 'jQuery(".w2p_flash").html("' + messagetxt + '").slideDown().delay(1500).slideUp(); $("#target").html("' \
       + messagetxt + '"); $("#btns' + str(questid) + ' .btn-success").addClass("disabled").removeClass("btn-success"); $("#btns'\
      + str(questid) + ' .btn-danger").addClass("disabled").removeClass("btn-danger");'
