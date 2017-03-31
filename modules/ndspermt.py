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


from gluon import *
import datetime


def get_groups(userid=None):
    """This should return a list of groups that a user has access to it now requires a login to
     be passed and currently only used on submit and questcountrows with user so no need to handle none
     :param userid: """

    accessgrouprows = current.db((current.db.group_members.auth_userid == userid)
                                 & (current.db.group_members.status == 'member')).select()
    access_group = [x.access_group.group_name for x in accessgrouprows]
    access_group.append('Unspecified')
    return access_group


def get_exclude_groups(userid=None):
    """This should return a list of groups that a user does not have access to it now requires a login to
     be passed and currently only used on submit and questcountrows with user so no need to handle none
     :param userid: """
    accessgroups = current.db(current.db.access_group.id > 0).select()
    allgroups = [x.group_name for x in accessgroups]
    exclude_group = list(set(allgroups) - set(get_groups(userid)))

    return exclude_group

# can view needs implemented

''' now have a few functions to think about here
    1) Can a user view a question?
        Change here is to have  a function check if question has a group then user must belong to that group
        think this is submitted with the group of the question - but potentially this can just be a call to get groups
        only required in viewquest for now
        So - this is can_view - will be part of ph7 

    2) Can a user join a group?
        Yes if public, otherwise could apply if apply and won't see groups that are invite only or admin unless they are
        already members of them - need to figure out options for each group
        implemented as join_group

    3) Can a user edit a group?
        Yes if the owner or an admin of the group and one admin can appoint others
        to implement as group_actions

    4) Can a user delete a group?
        Only possible by the owner and if no questions are assigned - otherwise deactivate
        to implement as group_actions        

    5) Can a user add a question/action or issue to an event?
        Yes if event is shared or they are the owner of the event - however question needs to be unassigned to another
        event

    6) Can a user submit a question to a group?
        Yes if member of the group - otherwise no - so no function required at present
        Test ph4_5 - not sure what the error will be

    7) Can a user answer a question, action or issue?
        Yes unless group policy blocks selecting questions to answer - and currently putting through the can_view
        routine first but this may need an answerable function

    8) Can a user vote on a question
        Yes if part of group that question assigned to and haven't voted before - not clear if we should allow change of
        mind - but no obvious reason not to

Above will do for now - in general we cant use decorated functions for these as need to evaluate which event, question
etc the user is attempting to answer/view

    Whole approach to votes in progress is probably missing bit of the framework now - but think votes are completely
    separate as they have expiry dates and so forth - and they can change from one to the other - possibly until
    resolved - would just be a question of updating the count - but lets keep separate for now - so it can be a
    dimension - lets start to get that in place

'''


def can_view(status, resolvemethod, hasanswered, answer_group, duedate, userid, owner):
    """Will be some doctests on this in due course and a table of condtions
    Basic rules are that for votes users can't see questions that they haven't answered
    vote style questions can be seen after expiry and never before and users can never see
    questions for groups they don't belong to.
    """

    viewable = False
    message = ''
    reason = 'OK to view'

    access_groups = get_groups(userid)

    if answer_group in access_groups:
        if userid == owner:  # think always allow owners to view questions whether votes or not
            viewable = True
        elif (status == 'In Progress' or status == 'Draft') and hasanswered is False:
            message = "You can't view this question as it's not resolved and you haven't answered it."
            reason = 'NotAnswered'
        elif get_resolve_method(resolvemethod) == 'Vote' and duedate > datetime.datetime.now():
            message = "Vote is still in progress and policy is not to show until counted.  The vote ends at " +\
                      str(duedate)
            reason = 'VoteInProg'
        else:
            viewable = True
    else:
        message = "You do not have permission to view this item"
        reason = 'NotInGroup'

    return viewable, reason, message


def can_edit_plan(user, owner, shared, editors):
    if shared:
        can_edit = True
    elif user == owner:
        can_edit = True
    elif editors and user in editors:
        can_edit = True
    else:
        can_edit = False
    return can_edit
    

def get_resolve_method(questmethod):
    resolverecord = current.db(current.db.resolve.resolve_name == questmethod).select().first()
    if resolverecord:
        return resolverecord.resolve_method
    else:
        return 'Not Known'


def join_groups(userid):
    """This should return a list of groups that a user has access to it now requires a login to
     be passed and currently only used on submit and questcountrows with user so no need to handle none"""

    accessgrouprows = current.db(current.db.group_members.auth_userid == userid).select()
    access_group = [x.access_group.group_name for x in accessgrouprows]
    access_group.append('Unspecified')
    return access_group


def get_actions(status, owner, userid, context):
    avail_actions = []
    if status == 'Complete' and userid is not None:
        avail_actions = ['Review']
    elif status == 'Draft' and owner == userid:
        avail_actions = ['Edit']
    if context == 'View':
        avail_actions.append('Next_Item')
    elif context == 'Submit':
        avail_actions.append('Link_Item')
        avail_actions.append('Add_Details')
        avail_actions.append('Add_Pictures')
    return avail_actions


def get_plan_actions(qtype, status, resolvemethod, owner, userid, hasanswered, context='std', eventid=0, shared=False, editors=None):
    avail_actions = []
    if can_edit_plan(userid, owner, shared, editors):
        avail_actions = ['PlanEdit']
        if status != 'Completed':
            avail_actions.append('Complete')
    avail_actions.append('PlanView')
    return avail_actions
    

def make_button(action, id, context='std', rectype='quest', eventid=0, questid=0):
    """This should return a button with appropriate classes for an action in a given context this will typiclly 
       be called by a get_buttons function which will take call get actions to get the actions and then make
       a button for each action There are currently 9 possible actions in the get_actions list:
       Approve, Disapprove, Pass and Reject for quick resolution and
       Agree, Disagree, Challenge and Details which are all currently setup on viewquest but not as TAG.INPUT

       So I think that is phase 1 and then put in as buttons -the structure of review is also worth looking at
    """

    # Below is result for call to link question to event
    session = current.session
    stdclass = "btn btn-primary btn-xs btn-group-xs"
    warnclass = "btn btn-warning btn-xs btn-group-xs"
    successclass = "btn btn-success btn-xs btn-group-xs"
    if action == 'Other':
        stringlink = XML("ajax('" + URL('viewquest', 'agree', args=[id, 1]) + "' , ['quest'], ':eval')")
        buttonhtml = TAG.INPUT(_TYPE='BUTTON', _class="btn btn-success  btn-xs btn-group-xs", _onclick=stringlink, _VALUE="Review")
    elif action == 'Disagree':
        stringlink = XML("ajax('" + URL('viewquest', 'agree', args=[id, 2]) + "' , ['quest'], ':eval')")
        buttonhtml = TAG.INPUT(_TYPE='BUTTON', _class="btn btn-danger  btn-xs btn-group-xs", _onclick=stringlink, _VALUE="Disagree")
    elif action == 'Approve':
        stringlink = XML("ajax('" + URL('answer','quickanswer', args=[id, 0]) + "', ['quest'], ':eval')")
        buttonhtml = TAG.INPUT(_TYPE='BUTTON', _class="btn btn-success  btn-xs btn-group-xs", _onclick=stringlink, _VALUE="Approve")
    elif action == 'Not Review':
        stringlink = XML("ajax('" + URL('answer', 'quickanswer', args=[id, 1]) + "', ['quest'], ':eval')")
        buttonhtml = TAG.INPUT(_TYPE='BUTTON', _class="btn btn-danger  btn-xs btn-group-xs", _onclick=stringlink, _VALUE="Disapprove")
    elif action == 'Review':
        stringlink = XML(
                "parent.location='" + URL('answer', 'answer_question', args=[id], extension='html') + "'")
        buttonhtml = TAG.INPUT(_TYPE='BUTTON', _class=stdclass, _onclick=stringlink, _VALUE="Review")
    elif action == 'Create_Action':
        stringlink = XML("parent.location='" + URL('submit', 'new_question', args=['action'], extension='html') + "'")
        buttonhtml = TAG.INPUT(_TYPE='BUTTON', _class=stdclass, _onclick=stringlink, _VALUE="Create Action")
    else:
        buttonhtml = XML("<p>Button not setup</p>")

    return buttonhtml


def get_buttons(status, id, owner, userid, hasanswered=False, context='default'):
    avail_actions = get_actions(status, owner, userid, context)
    print avail_actions
    return butt_html(avail_actions, context, id, 'activity')


def get_plan_buttons(qtype, status, resolvemethod,  id, owner, userid, hasanswered=False, context='std', eventid=0, shared=False, editors=None):
    avail_actions = get_plan_actions(qtype, status, get_resolve_method(resolvemethod), owner, userid, hasanswered,
                                     context, eventid, shared, editors)
    return butt_html(avail_actions, context, id, 'quest', eventid)
    

def get_locn_buttons(locid, shared, owner, userid, context='std'):
    avail_actions = get_locn_actions(locid, shared, owner, userid, context)
    return butt_html(avail_actions, context, locid, 'location')


def get_group_buttons(groupid, group_type, group_owner, userid, member=False, context='std'):
    avail_actions = get_group_actions(groupid, group_type, group_owner, userid, member)
    if avail_actions:
        return butt_html(avail_actions, context, groupid, 'group')
    else:
        return 'None'


def butt_html(avail_actions, context, id, rectype, eventid=0, questid=0):
    buttonhtml = False
    for x in avail_actions:
        if buttonhtml:
            buttonhtml += make_button(x, id, context, rectype, eventid, questid)
            buttonhtml += '\r'
        else:
            buttonhtml = make_button(x, id, context, rectype, eventid, questid)
            buttonhtml += '\r'
    return buttonhtml


def get_group_actions(groupid, group_type, group_owner, userid, member=False, context='std'):
    avail_actions = []
    if group_type in ['all', 'public', 'apply']:
        if member:
            if not group_owner == userid:
                avail_actions.append('Leave_Group')
        else:
            avail_actions.append('Join_Group')
    if group_owner == userid:
        avail_actions.append('Edit_Group')
        avail_actions.append('Group_Members')
    return avail_actions


def get_member_actions(status, owner):
    avail_actions = []
    if status == 'pending':
        avail_actions.append('Accept_User')
        avail_actions.append('Reject_User')
    elif status == 'member' and not owner:
        avail_actions.append('Block_User')
        avail_actions.append('Delete_User')
    elif status == 'blocked':
        avail_actions.append('Accept_User')
    return avail_actions


def get_locn_actions(locid, shared, owner, userid, context='std'):
    avail_actions = ['View_Location']
    if shared is True or owner == userid:
        avail_actions.append('Add_Event_Location')
    if owner == userid:
        avail_actions.append('Edit_Location')
    return avail_actions


def get_proj_actions(projid, shared, owner, userid, context='std'):
    avail_actions = ['View_Project']
    if shared is True or owner == userid:
        avail_actions.append('Add_Event_Project')
        avail_actions.append('Add_Item_Project')
    if owner == userid:
        avail_actions.append('Edit_Project')
    if context != 'projectmap':
        avail_actions.append('Projectmap')
    return avail_actions


def get_event_actions(eventid, shared, owner, userid, context='std', status='Open', nextevent=0, prevevent=0):
    avail_actions = []
    if status != 'Archived':
        if context != 'viewevent':
            avail_actions.append('View_Event')
        if shared is True or owner == userid:
            avail_actions.append('Add_Issue')
            avail_actions.append('Add_Quest')
            avail_actions.append('Add_Action')
            avail_actions.append('Link_Items')
            avail_actions.append('Export_Event')
            if nextevent:
                avail_actions.append('Next_Event')
            else:
                avail_actions.append('Create_Next')
            if prevevent:
                avail_actions.append('Prev_Event')
        if owner == userid:
            avail_actions.append('Edit_Event')
            if context == 'eventreview' or context == 'viewevent':
                avail_actions.append('Archive')             # only editable once status moves to archiving and owner
        if context == 'eventmap':
            avail_actions.append('Redraw')
        avail_actions.append('Event_Answer')
    if context != 'eventreview' and status == 'Archiving':
        avail_actions.append('eventreview')
    if context != 'eventmap':
        avail_actions.append('Eventmap')

    return avail_actions
