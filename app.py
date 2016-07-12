"""Run a test server."""
from botos import app
from botos import login_manager
from botos.modules.admin import views
from botos.modules.voting import views

login_manager.login_view = 'login'

app.run(host='0.0.0.0', port=8080, debug=True)
