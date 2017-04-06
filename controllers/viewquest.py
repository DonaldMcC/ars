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

"""
 This controller handles viewing the full details on questions if allowed
 and also displaying the reason you are not allowed to view the question
 the functionality to submit a challenge is also included in this controller
 and that is called via ajax from the view of the question detail
 The three functions are:
 index:  displays the question details
 comments: add comments
 useranswers: shows detail of the useranswers -
 notshowing: explains why the question can't be displayed - actions should always be displayed
 challenge: allows submission of a challenge and return of whether this is allowed
 via ajax
 agree - ajax agreement or disagreement
 challenge - ajax submission to challenge
 flagcomment -
 urgency - ajax update urgency of item

 For actions not generally interested in user's views but would like these to be capable
 of prioritisation at any stage - need to see the date and will be some options to generate
 emails based on actions and also to challenge resolved actions to return them to proposed
 A separate comments function has now been created

    exposes:
    http://..../[app]/viewquest/index which has action, issue and question views
    http://..../[app]/viewquest/end_vote  #  Ajax call
    http://..../[app]/viewquest/useranswers
    http://..../[app]/viewquest/notshowing   
    http://..../[app]/viewquest/comments
    http://..../[app]/viewquest/challenge  #  Ajax call
    http://..../[app]/viewquest/agree  #  Ajax call
    http://..../[app]/viewquest/flagcomment  #  Ajax call
    http://..../[app]/viewquest/urgency  #  Ajax call

    """

from ndsfunctions import updatequestcounts
# from ndspermt import can_view
# from time import strftime
# import gluon.contrib.simplejson


def index():
    # This will be a general view on question details and it will require the
    # question id as an argument Logic will be to only display the question if it
    # has been submitted, resolved or answered/passed by the user
    # This maintains the general privacy approach to questions that may be
    # subject to answer eventually if resolved then there will be a view option
    # However approach for actions is different - they can be viewed at any time
    # but the buttons at the bottom should be very simlar

    # initialize variables as not used if action
    viewtext = ''
    votetext = ''
    numpass = 0
    uqanswered = False
    uqrating = 5
    uqimpact = 5
    uqans = 0
    newansjson = ''

    activities = db(db.activity.id == request.args(0, cast=int, default=0)).select() or \
                redirect(URL('notshowing/' + 'NoActivity'))
    activity = activities.first()

    uq = None

    if auth.user:
        uqs = db((db.user_rating.auth_userid == auth.user.id) & (db.user_rating.activityid == activity.id)).select()
        if uqs:
            uqanswered = True
            uq = uqs.first()

    #viewable = can_view(quest.status, quest.resolvemethod, uqanswered, quest.answer_group,
    #                    quest.duedate, auth.user_id, quest.auth_userid)

    if uqanswered:
        uqrating = uq.rating
        uqimpact = uq.impact

    return dict(activity=activity, viewtext=viewtext, uqanswered=uqanswered, uqrating=uqrating, uqimpact=uqimpact)


def comments():
    # This will be a general view on question comments it will require the
    # question id as an argument Logic will be to only display the comements if it
    # has been resolved
    # This maintains the general privacy approach to questions that may be
    # subject to answer eventually if resolved then there will be a view option
    # this needs the as_dict() treatment as well but lets debug viewquest first
    # and then do next - potentially this can be replaced with a plugin

    questid = request.args(0, cast=int, default=0) or redirect(URL('default', 'index'))

    session.questid = questid
    quest = db.question[questid]

    if quest is None:
        redirect(URL('viewquest', 'notshowing/' + 'NoQuestion'))

    return dict(quest=quest)


def useranswers():
    # This displays all users answers to the question and challenges if any
    # for now will probably display all challenges at the bottom of the page
    # as assumption is there won't be too many of these
    # looks like this also needs as_dict treatment

    items_per_page = 8
    questid = request.args(0, cast=int, default=0) or redirect(URL('default', 'index'))

    session.questid = questid
    quest = db.question[questid] or redirect(URL('viewquest', 'notshowing/' + 'NoQuestion'))
    # this needs to become a function - duplicated code with viewquest
    mastlstanswers = quest['answers']
    mastlstnumanswers = quest['answercounts']

    page = request.args(1, cast=int, default=0)
    limitby = (page * items_per_page, (page + 1) * items_per_page + 1)

    uqs = db(db.userquestion.questionid == questid).select(orderby=[~db.userquestion.uq_level], limitby=limitby)
    challs = db(db.questchallenge.questionid == questid).select(orderby=[~db.questchallenge.challengedate])

    return dict(quest=quest, uqs=uqs, page=page, items_per_page=items_per_page, challs=challs)


def notshowing():
    questid = request.args(1)
    shortreason = request.args(0)

    if shortreason == 'NotResolved':
        reason = "This question is not yet resolved and you haven't answered it"
    elif shortreason == 'NotAnswered':
        reason = 'You have not answered this question'
    elif shortreason == 'NotInGroup':
        reason = 'You do not have permission to view this item'
    elif shortreason == 'VoteInProg':
        quest = db(db.question.id == questid).select(db.question.duedate).first()
        reason = "Vote is still in progress so you can't see results. The vote concludes at " + str(quest.duedate)
    elif shortreason == 'NoQuestion':
        reason = 'This question does not exist'
    else:
        reason = 'Not Known'
    return dict(reason=reason, questid=questid, shortreason=shortreason)


def agree():
    # This allows users to record if they agree or disagree with resolve questions
    # - whether or not they have answered them - only resolved questions can
    # be agreed or disagreed with

    chquestid = request.args[0]
    agreeval = int(request.args[1])

    # arg is 1 for agreement and 0 for disagreement and we will use this as latest status
    # for the user and also as the reference for agreementcounts which may become a list int
    # field and then increment the pointer

    if auth.user is None:
        responsetext = 'You must be logged in to record agreement or disagreement'
    else:
        quest = db(db.question.id == chquestid).select().first()
        othcounts = quest.othercounts

        # find out if user has previously agreeed the question -
        # this will be a userchallenge record
        qc = db((db.questagreement.auth_userid == auth.user.id) &
                (db.questagreement.questionid == chquestid)).select().first()

        if qc is None:
            db.questagreement.insert(questionid=chquestid,
                                     auth_userid=auth.user.id, agree=agreeval)
            # Now also need to add 1 to the numagreement or disagreement figure
            # It shouldn't be possible to challenge unless resolved

            if agreeval == 1:
                othcounts[3] += 1
                responsetext = 'Agreement Recorded'
            else:
                othcounts[4] += 1
                responsetext = 'Disagreement Recorded'
        else:
            if agreeval == qc.agree:
                if agreeval == 1:
                    responsetext = 'You have already registered agreement'
                else:
                    responsetext = 'You have already registered your disagreement'
                    ' - you may be able to challenge'
            else:
                if agreeval == 1:
                    responsetext = 'Your vote has been changed to agreement'
                    othcounts[3] += 1
                    othcounts[4] -= 1
                else:
                    responsetext = 'Your vote has been changed to disagreement'
                    othcounts[3] -= 1
                    othcounts[4] += 1
                qc.update_record(agree=agreeval)

        db(db.question.id == chquestid).update(othercounts=othcounts)
    #return 'jQuery(".flash").html("' + responsetext + '").slideDown().delay(1500).slideUp();' \
    #                                                  ' $("#target").html("' + responsetext + '");'

    return 'jQuery(".w2p_flash").html("' + responsetext + '").slideDown().delay(1500).slideUp(); $("#target").html("' \
       + responsetext + '"); $("#btns' + str(chquestid) + ' .btn-success").addClass("disabled").removeClass("btn-success"); $("#btns'\
      + str(chquestid) + ' .btn-danger").addClass("disabled").removeClass("btn-danger");'


def flagcomment():
    # This allows users to record if they think a comment is inappropriate
    # if 3 separate users flag the comment then it is removed from display
    # permanently for now

    commentid = request.args[0]
    requesttype = request.args[1]

    if auth.user is None:
        responsetext = 'You must be logged in to flage inappropriate comments'
    else:
        comment = db(db.questcomment.id == commentid).select().first()

        if requesttype != 'admin':
            # check if user has previously challenged the question -
            # this will be an entry in the usersreject field

            if comment.usersreject is not None and auth.user.id in comment.usersreject:
                responsetext = 'You have already flagged this comment'
            else:
                responsetext = 'Rejection recorded'
                comment.numreject += 1
                if comment.usersreject is not None:
                    comment.usersreject.append(auth.user.id)
                else:
                    comment.usersreject = [auth.user.id]
                if comment.numreject > 2:
                    comment.status = 'NOK'
                comment.update_record()
        else:
            responsetext = 'Admin hide successful'
            comment.update_record(status='NOK')
    return responsetext


def urgency():
    # This allows users to record or update their assessment of the urgency and
    # importance of an action as this helps with prioritising the actions that
    # are required - next step is to attempt to get the view sorted and will
    # retrieve this as part of main index controller

    if request.vars.urgslider2 is None:
        urgslider = 5
    else:
        urgslider = int(request.vars.urgslider2)

    if request.vars.impslider2 is None:

        impslider = 5
    else:
        impslider = int(request.vars.impslider2)

    chquestid = request.args[0]
    if auth.user is None:
        responsetext = 'You must be logged in to record urgency and importance'
    else:
        questrows = db(db.question.id == chquestid).select()
        quest = questrows.first()
        qurgency = quest.urgency
        qimportance = quest.importance

        # find out if user has rated the question already
        qcs = db((db.questurgency.auth_userid == auth.user.id) &
                 (db.questurgency.questionid == chquestid)).select()

        qc = qcs.first()

        if qc is None:
            db.questurgency.insert(questionid=chquestid,
                                   auth_userid=auth.user.id,
                                   urgency=urgslider,
                                   importance=impslider)

            urgency = request.vars.urgslider2
            responsetext = 'Your assessment has been recorded'

        else:
            qc.update_record(urgency=request.vars.urgslider2,
                             importance=request.vars.impslider2)
            responsetext = 'Your assessment has been updated'

        if quest.totratings == 0:
            totratings = quest.totanswers()
        else:
            totratings = quest.totratings

        urgent = (((quest.urgency * totratings) + urgslider) / (totratings + 1))
        importance = (((quest.importance * totratings) + impslider) / (totratings + 1))

        if qc is None:
            totratings += 1
        priority = urgent * importance  # perhaps a bit arbitary but will do for now

        db(db.question.id == chquestid).update(urgency=urgent,
                                               importance=importance, priority=priority, totratings=totratings)

    return responsetext
