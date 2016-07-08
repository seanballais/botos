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

import settings

from botos.modules.people_info import controllers
from botos import app
from botos.modules.activity_log import ActivityLogObservable


# Set up the logger
logger = ActivityLogObservable.ActivityLogObservable('admin_' + __name__)


@app.route('/admin/register/admin',
           methods=[
               'GET',
               'POST'
           ])
def register_admin():
    """
    Register an admin.

    :return: Load the register page in the admin for GET, reload page otherwise.
    """
    if request.method == 'GET':
        logger.add_log(20,
                       'Received GET request. Loading admin registration page.')
        return render_template(settings.BASE_DIR + 'templates/default/voting/admin/register.html')

    logger.add_log(20,
                   'Creating admin ' + request.form['username'] + '.'
                   )

    controllers.Voter.add([request.form['username']],
                          [request.form['password']],
                          [request.form['section_id']]
                          )

    logger.add_log(20,
                   'Created user ' + request.form['username'] + ' successfully.'
                   )

    flash('User ' + request.form['username'] + ' successfully created.')

    return redirect(url_for('admin_register_voter'))