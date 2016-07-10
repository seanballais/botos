# botos/modules/voting/views.py
# Copyright (C) 2016 Sean Francis N. Ballais
#
# This module is part of Botos and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php

""" Views for voting.

"""

from flask import request
from flask import render_template
from flask import Flask
from flask import session
from flask import flash
from flask import url_for
from flask import redirect
from flask import abort
from flask import g
from flask_login import login_user
from flask_login import logout_user
from flask_login import current_user
from flask_login import login_required

import settings

from botos.modules.people_info import controllers
from botos import app
from botos.modules.activity_log import ActivityLogObservable


# Set up the logger
logger = ActivityLogObservable.ActivityLogObservable('voting_' + __name__)


@app.route('/login')
def login():
    """
    Login the voters before voting.

    :return: Reloads if invalid user credentials, loads the voting page otherwise.
    """
    if request.method != 'POST':
        logger.add_log(30,
                       'User attempted to go to a non-page directory with a {0} request.'
                       'Redirecting to the index page.'.format(request.method)
                       )

        return redirect('/')

    voter_id = request.form['voter_id']
    password = request.form['password']
    logger.add_log(20,
                   'Attempting to log in voter ' + voter_id + '.'
                   )

    registered_voter = controllers.User.get_voter_pw(voter_id,
                                                     password
                                                     )
    if registered_voter is None:
        logger.add_log(20,
                       'Invalid credentials entered for voter {0}.'.format(voter_id)
                       )
        flash('Voter ID or password is invalid.',
              'error'
              )
        return redirect('/')

    login_user(registered_voter,
               remember=True
               )

    logger.add_log(20,
                   'Voter ' + voter_id + ' logged in successfully.'
                   )
    flash('Logged in successfully.')
    return redirect('/')


@app.route('/logout')
def logout():
    """
    Logout the voter from the application.

    :return: Redirect to the login page.
    """
    if request.method != 'POST':
        logger.add_log(30,
                       'User attempted to go to a non-page directory with a {0} request.'
                       'Redirecting to the index page.'.format(request.method)
                       )

        return redirect('/')

    logger.add_log(20,
                   'Logging out user.'
                   )
    logout_user()

    # TODO: Delete the voter as well.

    return redirect('/')


@app.route('/send_vote')
def send_vote():
    """
    Send the vote to the database.

    :return: Redirect the user to the index page.
    """
    if request.method != 'POST':
        logger.add_log(30,
                       'User attempted to go to a non-page directory with a {0} request.'
                       'Redirecting to the index page.'.format(request.method)
                       )

        return redirect('/')

    # TODO: Send votes to VoteStore.

    # Set the user inactive.


@app.route('/')
def index():
    """
    Index page of the whole app. This page will show different looks depending on the current user state.

    :return: Render the appropriate template depending on the user status.
    """
    logger.add_log(20,
                   'Accessing index page.'
                   )
    if current_user.is_authenticated():
        logger.add_log(20,
                       'Current user is authenticated. Displaying voting page.')

    logger.add_log(20,
                   'Current visitor is anonymous. Might need to say "Who you? You ain\'t my nigga."')
