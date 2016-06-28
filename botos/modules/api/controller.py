# botos/modules/api/models.py
# Copyright (C) 2016 Sean Francis N. Ballais
#
# This module is part of Botos and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php

"""Controllers that are used throughout the app

"""


from botos import db
from botos.modules.api import models


class Voter():
    """Handles the addition, deletion, and modification of voters."""

    @staticmethod
    def add(self,
            voter_id_list,
            password_list,
            section_id_list
            ):
        """
        Create a new voter.

        :param voter_id_list: ID of the voter (randomly generated).
        :param password_list: Password of the voter. (duh!)
        :param section_id_list: ID of the section of the voter. (Ugh! Duh!)
        """
        for _voter_id, _password, _section_id in voter_id_list, password_list, section_id_list:
            db.session.add(models.Voter(_voter_id,
                                        _password,
                                        _section_id
                                        )
                           )

        db.session.commit()

    @staticmethod
    def delete(self,
               voter_id_list
               ):
        """
        Delete a voter.

        :param voter_id_list: List of the voter IDs to be deleted
        """
        for _voter_id in voter_id_list:
            models.Voter.query.filter(models.Voter == _voter_id).delete()

        db.session.commit()

    @staticmethod
    def delete_all(self):
        """
        Delete all voters.
        """
        models.Voter.query.delete()
        db.session.commit()

    @staticmethod
    def modify_voter_id(self,
                        old_voter_id_list,
                        new_voter_id_list
                        ):
        """
        Modify voters' ID.

        :param old_voter_id_list: The IDs of the users that will be modified.
        :param new_voter_id_list: The new IDs of the users.
        """
        for _old_voter_id, _new_voter_id in old_voter_id_list, new_voter_id_list:
            _voter = models.Voter.query.filter_by(voter_id = _old_voter_id).first()
            _voter.voter_id = new_voter_id_list

            db.session.commit()

    @staticmethod
    def modify_voter_password(self,
                              voter_id_list,
                              new_password_list
                              ):
        """
        Modify voters' password

        :param voter_id_list: The IDs of the users that will be modified.
        :param new_password_list: The list of new passwords of each respective
            user.
        """
        for _voter_id, _password in voter_id_list, new_password_list:
            _voter = models.Voter.query.filter_by(voter_id = _voter_id).first()
            _voter.password = _password

        db.session.commit()

    @staticmethod
    def modify_voter_section(self,
                             voter_id_list,
                             section_id_list
                             ):
        """
        Modify voter's section.

        :param voter_id_list: The IDs of the users that will be modified.
        :param section_id_list: The list of new sections each user will have.
        """
        for _voter_id, _section_id in voter_id_list, section_id_list:
            _voter = models.Voter.query.filter_by(voter_d = _voter_id).first()
            _voter.section_id = _section_id

        db.session.commit()
