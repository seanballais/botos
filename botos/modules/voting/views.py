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
from flask import render_template
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


@app.route('/login',
           methods=[
               'GET',
               'POST'
           ])
def login():
    """
    Login the voters before voting.

    :return: Reloads if invalid user credentials, loads the voting page otherwise.
    """
    if request.method == 'GET':
        logger.add_log(20,
                       'Received GET request. Loading voter login page.')
        return render_template(settings.BASE_DIR + 'templates/default/voting/login.html')

    voter_id = request.form['voter_id']
    password = request.form['password']
    logger.add_log(20,
                   'Attempting to log in voter ' + voter_id + '.'
                   )

    registered_voter = controllers.Voter.get_voter(voter_id,
                                                   password
                                                   )
    if registered_voter is None:
        logger.add_log(20,
                       'Invalid credentials entered for voter {0}.'.format(voter_id)
                       )
        flash('Voter ID or password is invalid.',
              'error'
              )
        return redirect(url_for('login'))

    login_user(registered_voter,
               remember=True
               )

    logger.add_log(20,
                   'Voter ' + voter_id + ' logged in successfully.'
                   )
    flash('Logged in successfully.')
    return redirect(request.args.get('next') or url_for('index'))


@app.route('/logout')
def logout():
    """
    Logout the voter from the application.

    :return: Redirect to the login page.
    """
    # TODO: Send votes to the VoteStore module.

    logger.add_log(20,
                   'Logging out user.'
                   )
    logout_user()

    # TODO: Delete the voter as well.

    return redirect(url_for('index'))

# TODO: Add an index page that determines what page to load.