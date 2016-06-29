# botos/modules/api/models.py
# Copyright (C) 2016 Sean Francis N. Ballais
#
# This module is part of Botos and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php

"""Controllers that are used throughout the app

"""


from botos import db
from botos.modules.api import models


class Voter:
    """Handles the addition, deletion, and modification of voters."""

    @staticmethod
    def add(voter_id_list,
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
    def delete(voter_id_list
               ):
        """
        Delete a voter.

        :param voter_id_list: List of the voter IDs to be deleted
        """
        for _voter_id in voter_id_list:
            models.Voter.query.filter(models.Voter == _voter_id).delete()

        db.session.commit()

    @staticmethod
    def delete_all():
        """
        Delete all voters.
        """
        models.Voter.query.delete()
        db.session.commit()

    @staticmethod
    def modify_voter_id(old_voter_id_list,
                        new_voter_id_list
                        ):
        """
        Modify voters' ID.

        :param old_voter_id_list: The IDs of the users that will be modified.
        :param new_voter_id_list: The new IDs of the users.
        """
        for _old_voter_id, _new_voter_id in old_voter_id_list, new_voter_id_list:
            _voter = models.Voter.query.filter_by(voter_id=_old_voter_id).first()
            _voter.voter_id = new_voter_id_list

            db.session.commit()

    @staticmethod
    def modify_voter_password(voter_id_list,
                              new_password_list
                              ):
        """
        Modify voters' password

        :param voter_id_list: The IDs of the users that will be modified.
        :param new_password_list: The list of new passwords of each respective
            user.
        """
        for _voter_id, _password in voter_id_list, new_password_list:
            _voter = models.Voter.query.filter_by(voter_id=_voter_id).first()
            _voter.password = _password

        db.session.commit()

    @staticmethod
    def modify_voter_section(voter_id_list,
                             section_id_list
                             ):
        """
        Modify voter's section.

        :param voter_id_list: The IDs of the users that will be modified.
        :param section_id_list: The list of new sections each user will have.
        """
        for _voter_id, _section_id in voter_id_list, section_id_list:
            _voter = models.Voter.query.filter_by(voter_id=_voter_id).first()
            _voter.section_id = _section_id

        db.session.commit()


class VoterSection:
    """Handles the addition, deletion, and modification of voter sections."""

    @staticmethod
    def add(section_name_list,
            batch_id_list,
            ):
        """
        Create a new section.

        :param section_name_list: Name of the section.
        :param batch_id_list: ID of the batch where this section is under.
        """
        for _section_name, _batch_id in section_name_list, batch_id_list:
            db.session.add(models.VoterSection(_section_name,
                                               _batch_id
                                               )
                           )

        db.session.commit()

    @staticmethod
    def delete(section_list
               ):
        """
        Delete a number of sections.

        :param section_list: List containing the sections
        """
        for _section in section_list:
            models.VoterSection.query.filter_by(section_name=_section).delete()

        db.session.commit()

    @staticmethod
    def delete_all():
        """
        Delete all voter sections.
        """
        models.VoterSection.query.delete()
        db.session.commit()

    @staticmethod
    def modify_section_name(old_section_name_list,
                            new_section_name_list
                            ):
        """
        Modify the name of the section

        :param old_section_name_list: List containing the old names of the sections.
        :param new_section_name_list: List containing the new names of the sections.
        """
        for _old_section_name, _new_section_name in old_section_name_list, new_section_name_list:
            _section = models.VoterSection.query.filter_by(section_name=_old_section_name).first()
            _section.section_name = _new_section_name

        db.session.commit()

    @staticmethod
    def modify_section_batch(old_section_batch_list,
                             new_section_batch_list
                             ):
        """
        Modify the batch the section is under.

        :param old_section_batch_list: List of the old batch of the sections.
        :param new_section_batch_list: List of the new batch of the sections.
        """
        for _old_section_batch, _new_section_batch in old_section_batch_list, new_section_batch_list:
            _section = models.VoterSection.query.filter_by(section_name=_old_section_batch).first()
            _section.batch_id = _new_section_batch

        db.session.commit()


class VoterBatch:
    """Handles the addition, deletion, and modification of the batches."""

    @staticmethod
    def add(batch_name_list
            ):
        """
        Create a new batch.

        :param batch_name_list: List of new batches to be created.
        """
        for _batch_name in batch_name_list:
            db.session.add(models.VoterBatch(_batch_name))

        db.session.commit()

    @staticmethod
    def delete(batch_name_list
               ):
        """
        Delete batches.

        :param batch_name_list: List of batches to be deleted.
        """
        for _batch_name in batch_name_list:
            models.VoterBatch.query.filter_by(batch_name=_batch_name).delete()

        db.session.commit()

    @staticmethod
    def delete_all():
        """
        Delete all VoterBatches.
        """
        models.VoterBatch.query.delete()
        db.session.commit()

    @staticmethod
    def modify_batch_name(old_batch_name_list,
                          new_batch_name_list
                          ):
        """
        Modify the current names of a list of batches.

        :param old_batch_name_list: List of the old batches.
        :param new_batch_name_list: List of the new batch names.
        """
        for _old_batch_name, _new_batch_name in old_batch_name_list, new_batch_name_list:
            _batch = models.VoterBatch.query.filter_by(batch_name=_old_batch_name).first()
            _batch.batch_name = _new_batch_name

        db.session.commit()


class VoterSectionVotes:
    """Handles the addition, deletion, and updating of the sections and the votes."""

    @staticmethod
    def add(section_id_list,
            candidate_id_list
            ):
        """
        Create a new section vote record to handle the votes of a section.

        :param section_id_list: The IDs of the sections to be added.
        :param candidate_id_list: The IDs of the candidates where the
            section votes will be counted to.
        """
        for _section, _candidate in section_id_list, candidate_id_list:
            db.session.add(models.VoterSectionVotes(_section,
                                                    _candidate
                                                    )
                           )

        db.session.add()

    @staticmethod
    def delete_record(section_id_list
                      ):
        """
        Delete a voting record.

        :param section_id_list: The IDs of the sections in the records that
            will be deleted.
        """
        for _section in section_id_list:
            models.VoterSectionVotes.query.filter_by(section_id=_section).delete()

        db.session.commit()

    @staticmethod
    def delete_all():
        """
        Delete all voting records.
        """
        models.VoterSectionVotes.query.delete()
        db.session.commit()

    @staticmethod
    def modify_section(old_section_id_list,
                       new_section_id_list
                       ):
        """
        Modify the sections of a given record.

        :param old_section_id_list: The IDs of the section records to be modified.
        :param new_section_id_list: The new IDs of the section records.
        """
        for _old_section, _new_section in old_section_id_list, new_section_id_list:
            _section = models.VoterSectionVotes.query.filter_by(section_id=_old_section).first()
            _section.section_id = _new_section

        db.session.commit()

    @staticmethod
    def modify_section_candidate(section_id_list,
                                 candidate_id_list
                                 ):
        """
        Modify the candidates of the sections.

        :param section_id_list: The IDs of the section in which the candidate will
            be modified.
        :param candidate_id_list: The IDs of the new candidates of the sections.
        """
        for _section_id, _candidate in section_id_list, candidate_id_list:
            _section = models.VoterSectionVotes.query.filter_by(section_id=_section_id).first()
            _section.candidate_id = _candidate

        db.session.commit()

    @staticmethod
    def update_votes(section_id_list,
                     vote_delta_list
                     ):
        """
        Update votes (either decrement or increment them).

        :param section_id_list: The section IDs of which the votes will be updated.
        :param vote_delta_list: The change in the total votes.
        """
        for _section_id, _votes in section_id_list, vote_delta_list:
            _section = models.VoterSectionVotes.query.filter_by(section_id=_section_id).first()
            _section.votes += _votes  # Brexit :/

        db.session.commit()