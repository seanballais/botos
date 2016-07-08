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
from flask_login import login_user
from flask_login import logout_user
from flask_login import current_user
from flask_login import login_required

import string
import random

import settings

from botos.modules.people_info import controllers
from botos import app
from botos.modules.activity_log import ActivityLogObservable


# Set up the logger
logger = ActivityLogObservable.ActivityLogObservable('admin_' + __name__)


# TODO: Add AJAX call support.

@app.route('/admin/register/admin')
def register_admin():
    """
    Register an admin.

    :return: Reload the page once creation is done.
    """
    logger.add_log(20,
                   'Creating admin {0}.'.format(request.form['username'])
                   )

    controllers.Voter.add([request.form['username']],
                          [request.form['password']],
                          [request.form['section_id']]
                          )

    logger.add_log(20,
                   'Created user {0} successfully.'.format(request.form['username'])
                   )

    flash('User {0} successfully created.'.format(request.form['username']))

    return redirect(url_for('admin_register'))


@app.route('/admin/register/voters')
def register_voters():
    """
    Register voters and generate random voter IDs and passwords.

    :return: Reload the page once creation is done.
    """
    num_voters = request.form['num_voters']
    section_id = request.form['section_id']

    logger.add_log(20,
                   'Creating {0} new voters.'.format(num_voters)
                   )

    alphanum_str = string.digits + string.ascii_letters
    voter_list = []
    password_list = []
    for _ in xrange(num_voters):
        voter_id = ''
        password = ''
        logger.add_log(20,
                       'Generating a new voter.'
                       )
        for i in xrange(16):
            if i < 8:
                voter_id += random.choice(alphanum_str)

            password += random.choice(alphanum_str)

        logger.add_log(20,
                       'Generated voter {0}'.format(voter_id)
                       )

        voter_list.append(voter_id)
        password_list.append(password)

    logger.add_log(20,
                   'Creating the new set of randomly generated voters.'
                   )

    controllers.Voter.add(voter_list,
                          password_list,
                          [section_id] * num_voters
                          )

    success_msg = 'Successfully created {0} new voters.'.format(num_voters)
    logger.add_log(20,
                   success_msg
                   )

    flash(success_msg)

    return redirect(url_for('admin_register'))


@app.route(/admin/register/batch)


@app.route(/admin/register/section)


@app.route(/admin/register/candidate)
def register_candidate():
    """
    Register the candidate.

    :return:
    """


@app.route(/admin/register/party)


@app.route(/admin/register/position)