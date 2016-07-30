"""Run a test server."""
from flask import send_from_directory

from botos import app
from botos import login_manager
from botos.modules.admin import views
from botos.modules.voting import views
from botos.modules.app_data.controllers import Settings

import settings

login_manager.login_view = 'botos.modules.voting.views.app_index'


@app.route('/assets/<path:filename>',
           methods=[
               'GET',
               'POST'
           ])
def static_template_view(filename):
    return send_from_directory('{0}/botos/templates/{1}/static/'.format(app.config['BASE_DIR'],
                                                                        Settings.get_property_value('current_template')
                                                                        ),
                               filename
                               )


@app.route('/content/<path:filename>',
           methods=[
               'GET',
               'POST'
           ])
def static_content_view(filename):
    return send_from_directory('{0}/botos/botos-content/'.format(app.config['BASE_DIR']),
                               filename
                               )

app.run(host=settings.APP_HOST,
        port=settings.APP_PORT,
        debug=settings.DEBUG
        )
