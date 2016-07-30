# botos/modules/voting/views.py
# Copyright (C) 2016 Sean Francis N. Ballais
#
# This module is part of Botos and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php

""" Views for voting.

"""

from flask import request
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
        registered_user = controllers.User.get_user(username)

        if registered_user is not None and registered_user.is_password_correct(password):
            login_user(registered_user,
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
    flash('Something is wrong. Please enter both username and password',
          'error'
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
    if request.method != 'POST':
        logger.add_log(20,
                       'User attempted to go to a non-page directory with a {0} request.'
                       'Redirecting to the index page.'.format(request.method)
                       )

        return redirect('/')

    logger.add_log(20,
                   'Logging out user {0}.'.format(current_user.username)
                   )
    logout_user()

    # TODO: Delete the voter as well.

    return redirect('/')


@app.route('/send_vote',
           methods=[
               'POST'
           ])
def send_vote():
    """
    Send the vote to the database.

    :return: Redirect the user to the index page.
    """
    if request.method != 'POST':
        logger.add_log(20,
                       'User attempted to go to a non-page directory with a {0} request.'
                       'Redirecting to the index page.'.format(request.method)
                       )

        return redirect('/')

    # TODO: Send votes to VoteStore.

    # Delete the user


@app.route('/')
def app_index():
    """
    Index page of the whole app. This page will show different looks depending on the current user state.

    :return: Render the appropriate template depending on the user status.
    """
    login_form = LoginForm()

    # Generate the necessary form fields
    level_num = 1
    for position in Utility.get_position_list():
        candidate_list = []
        candidate_num = 0
        for candidate in controllers.Candidate.get_candidate_with_position(position[0]):
            item_content = Markup(
                "<a href=\"javascript:set_radio('{0}-{1}');\" "
                "class=\"radio-picture\" style=\"background: url('{2}') no"
                "-repeat scroll 0 0 white;\">&nbsp;</a>".format(level_num,
                                                                candidate_num,
                                                                candidate.profile_url
                                                                )
            )
            candidate_list.append((
                candidate.id,
                item_content
            ))

            candidate_num += 1

        setattr(VotingForm,
                '{0}'.format(position[0]),
                RadioField('{0}_choices'.format(position[1]),
                           validators=[DataRequired()],
                           choices=candidate_list,
                           render_kw={
                               'id': "{0}".format(position[1]),
                           })
                )

        level_num += 1

    voting_form = VotingForm()

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
        else:
            logger.add_log(20,
                           'Logged in user is a voter. Displaying the voting page.'
                           )
            return render_template('{0}/voting.html'.format(Settings.get_property_value('current_template')),
                                   voting_form=voting_form
                                   )

    logger.add_log(20,
                   'Current visitor is anonymous. Might need to say "Who you? You ain\'t my nigga."'
                   )

    # TODO: Make the index template.
    return render_template('{0}/index.html'.format(Settings.get_property_value('current_template')),
                           form=login_form
                           )
