"""Set up the models."""
from botos.modules.app_data.controllers import Settings

# Generate the settings table records.
if not Settings.property_exists('current_template'):
    Settings.add_property('current_template')
    Settings.set_property('current_template',
                          'default'
                          )