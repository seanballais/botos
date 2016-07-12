# botos/modules/app_settings/settings.py
# Copyright (C) 2016 Sean Francis N. Ballais
#
# This module is part of Botos and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php

"""Singleton for the app-wide settings.

"""


from botos import db
from botos.modules.activity_log import ActivityLogObservable


logger = ActivityLogObservable.ActivityLogObservable()


class SettingsModel(db.Model):
    """Key/value store for the settings."""
    key   = db.Column(db.String(64),
                      nullable=False,
                      unique=True
                      )
    value = db.Column(db.String(64),
                      nullable=False
                      )

    def __init__(self,
                 key,
                 value
                 ):
        """
        Initialize the settings model.

        :param key: Key of the settings property.
        :param value: Value of the settings property.
        """
        self.key   = key
        self.value = value


class Settings:
    """Singleton class for the settings."""

    settings = Settings()

    @staticmethod
    def get_instance():
        """
        Get the singleton instance of the settings.

        :return: Settings instance.
        """

        logger.add_log(10,
                       'Getting Settings singleton instance.'
                       )

        return Settings.settings

    @staticmethod
    def set_property(settings_property,
                     value
                     ):
        """
        Set a property in the settings.

        :param settings_property: A property in the settings.
        :param value: The new value of the property.
        """

        logger.add_log(30,
                       'Setting property {0} to a new value: {1}.'.format(settings_property,
                                                                          value
                                                                          )
                       )

    @staticmethod
    def get_property_value(settings_property):
        """
        Get the value of a property.

        :param settings_property: Property in the settings.
        :return: The property value
        """
        return SettingsModel.query.filter_by(key=settings_property).first().value

    @staticmethod
    def property_exists(settings_property):
        """
        Check whether a property exists.

        :param settings_property: Property in the settings.
        :return: True if the property exists, False otherwise.
        """
        return SettingsModel.query.filter_by(key=settings_property).first() is not None

    @staticmethod
    def add_property(settings_property):
        """
        Add new settings property.

        :param settings_property: Property in the settings.
        """
        db.session.add(SettingsModel(_property,
                                     ''
                                     )
                       )
        db.session.commit()

    @staticmethod
    def remove_property(settings_property):
        """
        Remove a settings property.

        :param settings_property: Property in the settings.
        """
        SettingsModel.query.filter(key == settings_property).delete()

        db.session.commit()


