# botos/modules/admin/views.py
# Copyright (C) 2016 Sean Francis N. Ballais
#
# This module is part of Botos and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php

"""View for voter administration like voter registration.

"""

from flask import request
from flask import flash
from flask import redirect
from flask import render_template
from flask_login import current_user
from flask_login import logout_user

import settings

from botos.modules.app_data import controllers
from botos import app
from botos.modules.activity_log import ActivityLogObservable
from botos.modules.app_data.controllers import Settings
from botos.modules.admin import controllers
from botos.modules.admin.forms import AdminCreationForm
from botos.modules.admin.forms import VoterCreationForm
from botos.modules.admin.forms import VoterSectionCreationForm


# Set up the logger
logger = ActivityLogObservable.ActivityLogObservable('admin_' + __name__)


# TODO: Add AJAX call support in the future.

@app.route('/admin/register/admin',
           methods=[
               'POST'
           ])
def register_admin():
    """
    Register an admin.

    :return: Return a JSON response.
    """
    admin_creation_form = AdminCreationForm()
    logger.add_log(20,
                   'Attempting to create admin {0}.'.format(request.form['username'])
                   )

    username = admin_creation_form.username.data
    password = admin_creation_form.password.data
    role     = admin_creation_form.role.data
    if admin_creation_form.validate_on_submit():
        admin = controllers.User.get_user(username)

        if admin is None:
            logger.add_log(20,
                           'Created admin {0} with role {1} successfully.'.format(username,
                                                                                  role
                                                                                  )
                           )

            controllers.User.add(username,
                                 password,
                                 '',
                                 role
                                 )

            flash('Created admin {0} successfully.'.format(username))

        else:
            logger.add_log(20,
                           'Admin {0} already exists.'.format(username)
                           )
            flash('Admin {0} already exists.'.format(username))

    return redirect('/admin')


@app.route('/admin/register/voters',
           methods=[
               'POST'
           ])
def register_voters():
    """
    Register voters and generate random voter IDs and passwords.

    :return: Return a JSON response.
    """
    # Generate voters
    voter_creation_form = VoterCreationForm()
    num_voters = voter_creation_form.num_voters.data
    section_id = voter_creation_form.section.data

    logger.add_log(20,
                   'Creating {0} new voters.'.format(num_voters)
                   )

    voter_generator = controllers.VoterGenerator()
    voter_generator.generate(num_voters,
                             section_id
                             )

    pdf_generator = controllers.VoterPDFGenerator(num_voters,
                                                  controllers.VoterSection.get_voter_section_by_id(section_id)
                                                  )
    pdf_generator.generate_entry_pdf(voter_generator.voter_list)

    success_msg = 'Successfully created {0} new voters.'.format(num_voters)
    logger.add_log(20,
                   success_msg
                   )

    flash(success_msg)
    flash('<a href="{0}" target="_blank">Download Voter List (PDF)</a>'.format(pdf_generator.filename))

    return '{ "message": "true" }'


@app.route('/admin/register/batch',
           methods=[
               'POST'
           ])
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


@app.route('/admin/register/section',
           methods=[
               'POST'
           ])
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


@app.route('/admin/register/candidate',
           methods=[
               'POST'
           ])
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


@app.route('/admin/register/party',
           methods=[
               'POST'
           ])
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


@app.route('/admin/register/position',
           methods=[
               'POST'
           ])
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


@app.route('/admin/logout',
           methods=[
               'POST'
           ])
def logout_admin():
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
def admin_index():
    """
    Index page for the admin. All tools will be shown here.

    :return: Render a template depending on whether the user is anonymous, an admin, or a voter.
    """
    admin_register_form = AdminCreationForm()
    voter_register_form = VoterCreationForm()
    logger.add_log(20,
                   'Accessing admin index page.'
                   )

    if current_user.is_authenticated:
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
                    '{0}/admin/index_admin.html'.format(Settings.get_property_value('current_template')),
                    admin_register_form=admin_register_form,
                    voter_register_form=voter_register_form
                )
            elif current_user.role == 'viewer':
                logger.add_log(20,
                               'Logged in user is a viewer. Render the vote statistics.'
                               )
                return render_template(
                    '{0}/admin/index_viewer.html'.format(Settings.get_property_value('current_template'))
                )

    logger.add_log(20,
                   'Current visitor is anonymous. Might need to say "Who you? You ain\'t my nigga. Identify!"'
                   )
    return redirect('/')