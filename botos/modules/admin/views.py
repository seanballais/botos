# botos/modules/admin/views.py
# Copyright (C) 2016 Sean Francis N. Ballais
#
# This module is part of Botos and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php

"""View for voter administration like voter registration.

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
from flask_login import current_user
from flask_login import login_user
from flask_login import logout_user

import string
import random

import settings

from botos.modules.people_info import controllers
from botos import app
from botos.modules.activity_log import ActivityLogObservable
from botos.modules.app_settings.settings import Settings


# Set up the logger
logger = ActivityLogObservable.ActivityLogObservable('admin_' + __name__)


# TODO: Add AJAX call support.

@app.route('/admin/register/admin')
def register_admin():
    """
    Register an admin.

    :return: Return a JSON response.
    """
    if request.method != 'POST':
        logger.add_log(20,
                       'User attempted to go to a non-page directory with a {0} request.'
                       'Redirecting to the index page.'.format(request.method)
                       )

        return redirect('/')

    logger.add_log(20,
                   'Creating admin {0}.'.format(request.form['username'])
                   )

    controllers.User.add(request.form['username'],
                         request.form['password'],
                         request.form['section_id'],
                         'admin'
                         )

    logger.add_log(20,
                   'Created user {0} successfully.'.format(request.form['username'])
                   )

    flash('User {0} successfully created.'.format(request.form['username']))

    return '{ "message": "true" }'


@app.route('/admin/register/voters')
def register_voters():
    """
    Register voters and generate random voter IDs and passwords.

    :return: Return a JSON response.
    """
    if request.method != 'POST':
        logger.add_log(20,
                       'User attempted to go to a non-page directory with a {0} request.'
                       'Redirecting to the index page.'.format(request.method)
                       )

        return redirect('/')

    # Generate voters
    num_voters = request.form['num_voters']
    section_id = request.form['section_id']

    logger.add_log(20,
                   'Creating {0} new voters.'.format(num_voters)
                   )

    alphanum_str = string.digits + string.ascii_letters
    for _ in range(num_voters):
        voter_id = ''
        password = ''
        logger.add_log(20,
                       'Generating a new voter.'
                       )
        for i in range(16):
            if i < 8:
                voter_id += random.choice(alphanum_str)

            password += random.choice(alphanum_str)

            # TODO: Add hashing and salting to the passwords.

        logger.add_log(20,
                       'Generated voter {0}'.format(voter_id)
                       )

        controllers.User.add(voter_id,
                             password,
                             section_id,
                             'voter'
                             )

    success_msg = 'Successfully created {0} new voters.'.format(num_voters)
    logger.add_log(20,
                   success_msg
                   )

    flash(success_msg)

    return '{ "message": "true" }'


@app.route('/admin/register/batch')
def register_batch():
    """
    Register a voter batch.

    :return: Return a JSON response.
    """
    if request.method != 'POST':
        logger.add_log(20,
                       'User attempted to go to a non-page directory with a {0} request.'
                       'Redirecting to the index page.'.format(request.method)
                       )

        return redirect('/')

    batch_name = request.form['batch_name']

    logger.add_log(20,
                   'Creating a batch {0}.'.format(batch_name)
                   )

    controllers.VoterBatch.add(batch_name)

    logger.add_log(20,
                   'Created batch {0} successfully.'.format(batch_name)
                   )

    flash('Batch {0} created successfully.'.format(batch_name))

    return '{ "message": "true" }'


@app.route('/admin/register/section')
def register_section():
    """
    Register a voter section.

    :return: Return a JSON response.
    """
    if request.method != 'POST':
        logger.add_log(20,
                       'User attempted to go to a non-page directory with a {0} request.'
                       'Redirecting to the index page.'.format(request.method)
                       )

        return redirect('/')

    section_name = request.form['section_name']
    batch_name = request.form['batch_name']

    logger.add_log(20,
                   'Creating a section {0} under {1}.'.format(section_name,
                                                              batch_name
                                                              )
                   )

    controllers.VoterSection.add(section_name,
                                 batch_name
                                 )

    logger.add_log(20,
                   'Created section {0} successfully.'.format(batch_name)
                   )

    flash('Section {0} created successfully.'.format(section_name))

    return '{ "message": "true" }'


@app.route('/admin/register/candidate')
def register_candidate():
    """
    Register a candidate.

    :return: Return a JSON response.
    """
    if request.method != 'POST':
        logger.add_log(20,
                       'User attempted to go to a non-page directory with a {0} request.'
                       'Redirecting to the index page.'.format(request.method)
                       )

        return redirect('/')

    candidate_first_name = request.form['Candidate_first-name']
    candidate_last_name = request.form['candidate_last_name']
    candidate_middle_name = request.form['candidate_middle_name']
    candidate_position = request.form['candidate_position']
    candidate_party = request.form['candidate_party']
    candidate_index = controllers.Candidate.get_next_index(candidate_position)

    logger.add_log(20,
                   'Creating candidate {0} {1} under {2}.'.format(candidate_first_name,
                                                                  candidate_last_name,
                                                                  candidate_party
                                                                  )
                   )

    controllers.Candidate.add(candidate_index,
                              candidate_first_name,
                              candidate_last_name,
                              candidate_middle_name,
                              candidate_position,
                              candidate_party
                              )

    logger.add_log(20,
                   'Created candidate {0} {1} successfully.'.format(candidate_first_name,
                                                                    candidate_last_name
                                                                    )
                   )

    flash('Candidate {0} {1} created successfully.'.format(candidate_first_name,
                                                           candidate_last_name
                                                           )
          )

    return '{ "message": "true" }'


@app.route('/admin/register/party')
def register_party():
    """
    Register a party.

    :return: Return a JSON response.
    """
    if request.method != 'POST':
        logger.add_log(20,
                       'User attempted to go to a non-page directory with a {0} request.'
                       'Redirecting to the index page.'.format(request.method)
                       )

        return redirect('/')

    party_name = request.form['party_name']

    logger.add_log(20,
                   'Creating party {0}.'.format(party_name)
                   )

    controllers.CandidateParty.add(party_name)

    logger.add_log(20,
                   'Created party {0} successfully.'.format(party_name)
                   )

    flash('Successfully created party {0}.'.format(party_name))

    return '{ "message": "true" }'


@app.route('/admin/register/position')
def register_position():
    """
    Register a position.

    :return: Return a JSON response.
    """
    if request.method != 'POST':
        logger.add_log(20,
                       'User attempted to go to a non-page directory with a {0} request.'
                       'Redirecting to the index page.'.format(request.method)
                       )

        return redirect('/')

    position_name = request.form['position_name']
    position_level = request.form['position_level']

    logger.add_log(20,
                   'Creating candidate position {0} at level {1}.'.format(position_name,
                                                                          position_level
                                                                          )
                   )

    controllers.CandidatePosition.add(position_name,
                                      position_level
                                      )

    logger.add_log(20,
                   'Created candidate position {0} at level {1}.'.format(position_name,
                                                                         position_level
                                                                         )
                   )

    flash('Successfully created candidate position {0} at level {1}.'.format(position_name,
                                                                             position_level
                                                                             )
          )

    return '{ "message": "true" }'


@app.route('/admin/login')
def login_admin():
    """
    Login the administrator. This will log out any currently logged in voters.

    :return: Redirect to the index page if authenticated as a voter, reload otherwise.
    """
    if request.method != 'POST':
        logger.add_log(20,
                       'User attempted to go to a non-page directory with a {0} request.'
                       'Redirecting to the index page.'.format(request.method)
                       )

        return redirect('/')

    if current_user.is_authenticated():
        if current_user.role == 'voter':
            logger.add_log(20,
                           'Current user is logged in and a voter. '
                           )
            return redirect('/')
        return redirect('/admin')

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
        return redirect('/admin')

    if registered_user.role == 'voter':
        logger.add_log(30,
                       'Voter {0} has attempted to log in to the admin panel. Not on my watch.'.format(username)
                       )
        return redirect('/')

    login_user(registered_user,
               remember=True
               )

    logger.add_log(20,
                   'User {0} logged in successfully.'.format(username)
                   )
    flash('Logged in successfully.')

    return redirect('/admin')


@app.route('/admin/logout')
def logout():
    """
    Logout the admin from the application.

    :return: Redirect to the admin login page.
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

    return redirect('/admin')


@app.route('/admin')
def index():
    """
    Index page for the admin. All tools will be shown here.

    :return: Render a template depending on whether the user is anonymous, an admin, or a voter.
    """
    logger.add_log(20,
                   'Accessing admin index page.'
                   )

    if current_user.is_authenticated():
        logger.add_log(20,
                       'Current user is authenticated. Displaying voting page.')
        if current_user.role == 'voter':
            logger.add_log(20,
                           'Logged in user is a voter. Redirecting to the main voting page.'
                           )
            return redirect('/')
        else:
            if current_user.role == 'admin':
                logger.add_log(20,
                               'Logged in user is an admin. Render admin panel.'
                               )
                return render_template(
                    'templates/{0}/admin/index_admin.html'.format(Settings.get_property_value('current_template'))
                )
            elif current_user.role == 'viewer':
                logger.add_log(20,
                               'Logged in user is a viewer. Render the vote statistics.'
                               )
                return render_template(
                    'templates/{0}/admin/index_viewer.html'.format(Settings.get_property_value('current_template'))
                )

    logger.add_log(20,
                   'Current visitor is anonymous. Might need to say "Who you? You ain\'t my nigga. Identify!"'
                   )
    return render_template('templates/{0}/admin/login.html'.format(Settings.get_property_value('current_template')))