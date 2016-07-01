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
            _section.votes += _votes

        db.session.commit()


class Candidate:
    """Handles the addition, deletion, and modification of candidates."""

    @staticmethod
    def add(candidate_information_list):
        """
        Create a new candidate.

        :param candidate_information_list: Information about the candidate (Must be a list).
        """
        for _candidate in candidate_information_list:
            db.session.add(models.Candidate(candidate_idx=_candidate[0],
                                            first_name=_candidate[1],
                                            last_name=_candidate[2],
                                            middle_name=_candidate[3],
                                            position=_candidate[4],
                                            party=_candidate[5]
                                            )
                           )

        db.session.commit()

    @staticmethod
    def delete_candidate(candidate_id_list):
        """
        Delete candidates or a candidate from the database.

        :param candidate_id_list: The IDs of the candidates to be deleted.
        """
        for _id in candidate_id_list:
            models.Candidate.query.filter_by(candidate_id=_id).first().delete()

        db.session.commit()

    @staticmethod
    def delete_all():
        """
        Delete all candidates.
        """
        models.Candidate.query.delete()
        db.session.commit()

    @staticmethod
    def modify_candidate_index(candidate_id_list,
                               candidate_index_list
                               ):
        """
        Modify the index of the candidate with respect to the position in the voting page.

        :param candidate_id_list: The IDs of the candidates
        :param candidate_index_list: The new index of the candidates.
        """
        for _id, _index in candidate_id_list, candidate_index_list:
            _candidate = models.Candidate.query.filter_by(candidate_id=_id).first()
            _candidate.candidate_idx = _index

        db.session.commit()

    @staticmethod
    def modify_candidate_first_name(candidate_id_list,
                                    candidate_first_name_list
                                    ):
        """
        Modify the first name of the candidates.

        :param candidate_id_list: The IDs of the candidates.
        :param candidate_first_name_list: The new first names of the candidates.
        """
        for _id, _first_name in candidate_id_list, candidate_first_name_list:
            _candidate = models.Candidate.query.filter_by(candidate_id=_id).first()
            _candidate.first_name = _first_name

        db.session.commit()

    @staticmethod
    def modify_candidate_last_name(candidate_id_list,
                                   candidate_last_name_list
                                   ):
        """
        Modify the last name of the candidates.

        :param candidate_id_list: The IDs of the candidates.
        :param candidate_last_name_list: The new last names of the candidates.
        """
        for _id, _last_name in candidate_id_list, candidate_last_name_list:
            _candidate = models.Candidate.query.filter_by(candidate_id=_id).first()
            _candidate.last_name = _last_name

        db.session.commit()

    @staticmethod
    def modify_candidate_middle_name(candidate_id_list,
                                     candidate_middle_name_list
                                     ):
        """
        Modify the middle name of the candidates.

        :param candidate_id_list: The IDs of the candidates.
        :param candidate_middle_name_list: The new middle names of the candidates.
        """
        for _id, _middle_name in candidate_id_list, candidate_middle_name_list:
            _candidate = models.Candidate.query.filter_by(candidate_id=_id).first()
            _candidate.middle_name = _middle_name

        db.session.commit()

    @staticmethod
    def modify_candidate_position(candidate_id_list,
                                  candidate_position_list
                                  ):
        """
        Modify the position of the candidates.

        :param candidate_id_list: The IDs of the candidates.
        :param candidate_position_list: The new positions of the candidates.
        """
        for _id, _position in candidate_id_list, candidate_position_list:
            _candidate = models.Candidate.query.filter_by(candidate_id_list=_id).first()
            _candidate.position = _position

        db.session.commit()

    @staticmethod
    def modify_candidate_party(candidate_id_list,
                               candidate_party_list
                               ):
        """
        Modify the party of the candidates.

        :param candidate_id_list: The IDs of the candidates.
        :param candidate_party_list: The new parties of the candidates.
        """
        for _id, _party in candidate_id_list, candidate_party_list:
            _candidate = models.Candidate.query.filter_by(candidate_id=_id).first()
            _candidate.position = _party

        db.session.commit()


class CandidatePosition:
    """Handles the creation, deletion, and modification of candidate positions."""

    @staticmethod
    def add(position_name_list,
            position_level_list
            ):
        """
        Create a new candidate position.

        :param position_name_list: The name of the positions.
        :param position_level_list: The level of the positions.
        """
        for _name, _level in position_name_list, position_level_list:
            db.session.add(models.CandidatePosition(name=_name,
                                                    level=_level
                                                    )
                           )

        db.session.add()

    @staticmethod
    def delete_position(position_name_list):
        """
        Delete a position.

        :param position_name_list: The list containing the positions to be deleted.
        """
        for _name in position_name_list:
            models.CandidatePosition.query.filter_by(name=_name).first().delete()

        db.session.commit()

    @staticmethod
    def delete_all():
        """
        Delete all positions.
        """
        models.CandidatePosition.query.delete()
        db.session.commit()

    @staticmethod
    def modify_name(old_position_name_list,
                    new_position_name_list
                    ):
        """
        Modify the name of the positions.

        :param old_position_name_list: The old names of the positions.
        :param new_position_name_list: The new names of the positions.
        """
        for _old_name, _new_name in old_position_name_list, new_position_name_list:
            _position = models.CandidatePosition.query.filter_by(name=_old_name).first()
            _position.name = _new_name

        db.session.commit()

    @staticmethod
    def modify_level(position_name_list,
                     position_level_list
                     ):
        """
        Modify the level of the positions.

        :param position_name_list: The name of the position.
        :param position_level_list: The new level of the position.
        """
        for _name, _level in position_name_list, position_level_list:
            _position = models.CandidatePosition.query.filter_by(name=_name).first()
            _position.level = _level

        db.session.commit()