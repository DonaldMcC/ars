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

from ndsfunctions import score_question,  getitem
from ndspermt import get_exclude_groups


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

@auth.requires_login()
@auth.requires_signature()
def answer_question():
    """
    This allows the user to answer the question or pass and the result is 
    handled by the score question function.  This can really now be called
    from any event and it is an exposed url - so now need to check if not 
    resolved or already answered and if so we will not accept another answer
    """

    activityid = request.args(0, cast=int, default=0)
    activity = db(db.activity.id == activityid).select().first()

    ur = db((db.user_rating.activityid == activityid) & (db.user_rating.auth_userid == auth.user_id)).select().first()
    if ur:
        pass # TODO will insert record ID here and define fields above

    form2 = SQLFORM(db.user_activity, showid=False, fields=['rating', 'impact', 'reject'],
                    submit_button='Submit', col3={'reject': 'Select if invalid or off subject '},
                                                  formstyle='table3cols')

    form2.element(_type='submit')['_class'] = "btn btn-success"

    if ur: # already rated so will need to populate form vars with current values
    form2.vars.activescope = quest['activescope']
    form2.vars.continent = quest['continent']
    form2.vars.country = quest['country']
    form2.vars.subdivision = quest['subdivision']
    form2.vars.category = quest['category']


    if form2.validate():
        form2.vars.auth_userid = auth.user.id
        form2.vars.questionid = questid
        form2.vars.uq_level = quest['question_level']
        form2.vars.status = 'In Progress'
        # default to urgency 10 for testing so questions that are answered continue to get answered

        form2.vars.id = db.userquestion.insert(**dict(form2.vars))
        response.flash = 'form accepted'
        status = score_question(questid, form2.vars.id)
        if status == 'Resolved':
            scheduler.queue_task('send_email_resolved', pvars=dict(questid=questid), period=600)
        redirect(URL('viewquest', 'index', args=[questid, questtype]))
    elif form2.errors:
        response.flash = 'form has errors'

    return dict(form2=form2, quest=quest)


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
