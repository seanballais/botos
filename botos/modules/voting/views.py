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
from flask_login import login_user
from flask_login import logout_user
from flask_login import current_user

from botos.modules.app_data import controllers
from botos import app
from botos.modules.activity_log import ActivityLogObservable
from botos.modules.app_data.controllers import Settings
from botos.modules.voting.forms import LoginForm

# Set up the logger
logger = ActivityLogObservable.ActivityLogObservable('voting_' + __name__)


@app.route('/login',
           methods=[
               'POST'
           ])
def login():
    """
    Login the voters before voting.

    :return: Reloads if invalid user credentials, loads the voting page otherwise.
    """
    if request.method != 'POST':
        logger.add_log(20,
                       'User attempted to go to a non-page directory with a {0} request.'
                       'Redirecting to the index page.'.format(request.method)
                       )

        return redirect('/')

    username = request.form['username']
    password = request.form['password']
    logger.add_log(20,
                   'Attempting to log in user ' + username + '.'
                   )

    registered_user = controllers.User.get_voter_pw(username,
                                                    password
                                                    )
    if registered_user is None:
        logger.add_log(20,
                       'Invalid credentials entered for user {0}.'.format(username)
                       )
        flash('Username or password is invalid.',
              'error'
              )
        return redirect('/')

    login_user(registered_user,
               remember=True
               )

    logger.add_log(20,
                   'User {0} logged in successfully.'.format(username)
                   )
    flash('Logged in successfully.')

    if current_user.role == 'admin' or current_user.role == 'viewer':
        return redirect('/admin')

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

    logger.add_log(20,
                   'Current visitor is anonymous. Might need to say "Who you? You ain\'t my nigga."'
                   )

    # TODO: Make the index template.
    return render_template('{0}/index.html'.format(Settings.get_property_value('current_template')),
                           form=login_form
                           )
