# botos/modules/voting/views.py
# Copyright (C) 2016 Sean Francis N. Ballais
#
# This module is part of Botos and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php

""" Views for voting.

"""


import json
import collections

from flask import render_template
from flask import flash
from flask import redirect
from flask import Markup
from flask_login import login_user
from flask_login import logout_user
from flask_login import current_user
from wtforms import RadioField
from wtforms.validators import DataRequired

from botos.modules.app_data import controllers
from botos import app
from botos import login_manager
from botos.modules.activity_log import ActivityLogObservable
from botos.modules.app_data.controllers import Settings
from botos.modules.app_data.models import User
from botos.modules.admin.controllers import Utility
from botos.modules.voting.forms import LoginForm
from botos.modules.voting.forms import VotingForm

# Set up the logger
logger = ActivityLogObservable.ActivityLogObservable('voting_' + __name__)


def generate_voting_form():
    """
    Generate a voting form based on the information from the database.

    :return: Return a voting form with attributes based on the database.
    """
    logger.add_log(20,
                   'Generating voting form.'
                   )

    level_num = 1
    for position in Utility.get_position_list():
        candidate_list = []
        candidate_num = 0
        for candidate in controllers.Candidate.get_candidate_with_position(position[0]):
            logger.add_log(20,
                           'Generating candidate {0}.'.format(candidate.id)
                           )

            candidate_list.append((
                candidate.id,
                generate_option_images(level_num,
                                       candidate_num,
                                       candidate,
                                       position[0],
                                       controllers.CandidateParty.get_candidate_party_by_id(candidate.party).name
                                       )
            ))

            candidate_num += 1

        setattr(VotingForm,
                '{0}'.format(position[0]),
                RadioField(label=position[1],
                           validators=[DataRequired()],
                           choices=candidate_list,
                           render_kw={
                               'id': "{0}".format(position[1]),
                           })
                )
        level_num += 1

    return VotingForm()


def generate_option_images(level_num,
                           candidate_num,
                           candidate,
                           candidate_position,
                           candidate_party_name
                           ):
    """
    Generate option images for the candidates.

    :param level_num: Level of the candidate position.
    :param candidate_num: The nth candidate in the loop.
    :param candidate: Candidate dictionary.
    :param candidate_position: The position of the candidate.
    :param candidate_party_name: Party name of the candidate.
    :return: Return a markup of the option images.
    """
    return Markup(
        "<a href=\"javascript:void(0);\" id=\"{0}-{1}\" "
        "class=\"radio-picture {3}\" style=\"background: url('{2}') no"
        "-repeat scroll 0 0 white;\">&nbsp;</a><br/>"
        "<h3 class='candidate-name'>{4} {5}<br><small>{6}</small></h3>".format(level_num,
                                                                               candidate_num,
                                                                               candidate.profile_url,
                                                                               candidate_position,
                                                                               candidate.first_name,
                                                                               candidate.last_name,
                                                                               candidate_party_name
                                                                               )
    )


def generate_candidate_script_code(candidate_position):
    """
    Generate a JS script that will be used to add selection feedback.

    :param candidate_position: ID of the position of the candidate.
    :return: Return a markup string.
    """
    str_position = str(candidate_position)
    return Markup(
        '<script type="text/javascript">\n'
        '\t\t\t$("a.' + str_position + '").click(function() {\n'
        '\t\t\t\tvar input_clicked = $(this).parent().siblings("input");\n'
        '\t\t\t\tif (input_clicked.is(":checked")) {\n'
        'console.log("Clicked before.");'
        'console.log(input_clicked);'
        '\t\t\t\t\t$("a.' + str_position + '").removeClass("selected-glow");\n'
        '\t\t\t\t\tinput_clicked.prop("checked", false);\n'
        '\t\t\t\t} else {\n'
        'console.log("Oh really?");'
        'console.log(input_clicked);'
        '\t\t\t\t\tinput_clicked.prop("checked", true);\n'
        '\t\t\t\t\t$("a.' + str_position + '").removeClass("selected-glow");\n'
        '\t\t\t\t\t$(this).addClass("selected-glow");\n'
        '\t\t\t\t}\n'
        '\t\t\t})\n'
        '\t\t</script>\n'
    )


def generate_js_script():
    """
    Generate a JS script that will allow selection feedback on candidates.

    :return: Return a JS script.
    """
    js_link_handlers = []
    for position in Utility.get_position_list():
        js_link_handlers.append(generate_candidate_script_code(position[0]))

    return js_link_handlers


@login_manager.user_loader
def load_user(user_id):
    """
    Load the user. Callback for Flask-Login.

    :param user_id: ID of the user.
    :return: A User object.
    """
    logger.add_log(10,
                   'Getting user by ID of {0}.'.format(user_id)
                   )
    return User.query.get(user_id)


@app.route('/login',
           methods=[
               'POST'
           ])
def login():
    """
    Login the voters before voting.

    :return: Reloads if invalid user credentials, loads the voting page otherwise.
    """
    login_form = LoginForm()

    username = login_form.username.data
    password = login_form.password.data
    logger.add_log(20,
                   'Attempting to log in user {0}.'.format(username)
                   )

    if login_form.validate_on_submit():
        reg_user = controllers.User.get_user(username)

        if reg_user is not None and reg_user.is_password_correct(password) and reg_user.is_active():
            login_user(reg_user,
                       remember=True
                       )

            logger.add_log(20,
                           'User {0} logged in successfully.'.format(username)
                           )
            flash('Logged in successfully.')

            logger.add_log(10,
                           'Current user role: {0}'.format(current_user.role)
                           )
            if current_user.role == 'admin' or current_user.role == 'viewer':
                return redirect('/admin')

        else:
            logger.add_log(20,
                           'Invalid credentials entered for user {0}.'.format(username)
                           )

            flash('Username or password is invalid.',
                  'error'
                 )

            return redirect('/')

    logger.add_log(20,
                   'Username or password not entered.'
                   )

    return redirect('/')


@app.route('/logout',
           methods=[
               'POST'
           ])
def logout_voter():
    """
    Logout the voter from the application.

    :return: Redirect to the login page.
    """
    logger.add_log(20,
                   'Logging out user {0}.'.format(current_user.username)
                   )

    logout_user()

    return redirect('/')


@app.route('/send_vote',
           methods=[
               'POST'
           ])
def send_vote():
    """
    Send the vote to the database.

    :return: Redirect the user to the thank you page.
    """
    form = generate_voting_form()
    for field in form:
        if field.type != 'CSRFTokenField' and field.data != 'None':
            logger.add_log(20,
                           'Passing in voter data. Voting for candidate {0}'.format(field.data)
                           )
            controllers.VoteStore.increment_vote(field.data,
                                                 current_user.section_id
                                                 )

    controllers.User.set_active(current_user.username,
                                False
                                )

    return redirect('/thank_you')


@app.route('/get_votes',
           methods=[
               'POST',
               'GET'
           ])
def get_votes():
    """
    Get the current votes in the system.

    :return: Return a JSON string containing the latest votes of each candidate.
    """
    vote_data = collections.OrderedDict()
    for position in Utility.get_position_list():
        candidate_votes = collections.OrderedDict()
        candidate_count = 0
        for candidate in Utility.get_candidate_of_position_list(position[0]):
            total_votes = controllers.VoteStore.get_candidate_total_votes(candidate['id'])
            candidate_votes[candidate_count] = {
                'votes': total_votes,
                'name': "{0} {1} ({2})".format(candidate['first_name'],
                                               candidate['last_name'],
                                               position[1]
                                               ),
                'profile_url': "{0}".format(candidate['profile_url'])
            }

            candidate_count += 1

        vote_data[position[1]] = candidate_votes

    return json.dumps(vote_data)


@app.route('/thank_you')
def vote_thank_you():
    """
    Display the thank you page.

    :return: Render the thank you page.
    """
    if not current_user.is_active():
        logger.add_log(20,
                       'Voter {0} finished voting. Accessing thank you page.'.format(current_user.id)
                       )

        return render_template('{0}/thank-you.html'.format(Settings.get_property_value('current_template')))

    logger.add_log(20,
                   'Someone attempted to visit the thank you. Not sure if it was a voter, admin, or someone anonymous.'
                   )

    return redirect('/')


@app.route('/')
def app_index():
    """
    Index page of the whole app. This page will show different looks depending on the current user state.

    :return: Render the appropriate template depending on the user status.
    """
    login_form = LoginForm()

    logger.add_log(20,
                   'Accessing index page.'
                   )

    if current_user.is_authenticated:
        logger.add_log(20,
                       'Current user is authenticated. Displaying voting page.')
        if current_user.role != 'voter':
            logger.add_log(20,
                           'Logged in user is an admin. Redirecting to the admin panel.'
                           )
            return redirect('/admin')
        elif current_user.is_active():
            logger.add_log(20,
                           'Logged in user is a voter. Displaying the voting page.'
                           )
            return render_template('{0}/voting.html'.format(Settings.get_property_value('current_template')),
                                   voting_form=generate_voting_form(),
                                   link_handler=generate_js_script()
                                   )

    logger.add_log(20,
                   'Current visitor is anonymous or inactive. Might need to say "Who you? You ain\'t my nigga."'
                   )

    # TODO: Make the index template.
    return render_template('{0}/index.html'.format(Settings.get_property_value('current_template')),
                           form=login_form
                           )
