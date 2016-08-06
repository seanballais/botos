# botos/modules/people_info/controllers.py
# Copyright (C) 2016 Sean Francis N. Ballais
#
# This module is part of Botos and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php

"""Controllers that are used throughout the app

"""


from sqlalchemy.sql import func

from botos import db
from botos.modules.activity_log import ActivityLogObservable
from botos.modules.app_data import models


logger = ActivityLogObservable.ActivityLogObservable('app_data_' + __name__)


class User:
    """Handles the addition, deletion, and modification of voters."""

    @staticmethod
    def add(username,
            password,
            section_id,
            role
            ):
        """
        Create a new voter.

        :param username: username of the voter (randomly generated for voters).
        :param password: Password of the voter. (duh!)
        :param section_id: ID of the section of the voter. (Ugh! Duh!)
        :param role: Role of the user.
        """
        db.session.add(models.User(username,
                                   password,
                                   section_id,
                                   role,
                                   active=True
                                   )
                       )

        db.session.commit()

    @staticmethod
    def delete(username
               ):
        """
        Delete a voter.

        :param username: Username to be deleted
        """
        models.User.query.filter(models.User == username).delete()

        db.session.commit()

    @staticmethod
    def delete_all():
        """
        Delete all users.
        """
        models.User.query.delete()
        db.session.commit()

    @staticmethod
    def modify_username_id(old_username,
                           new_username
                           ):
        """
        Modify user names.

        :param old_username: The username of the user that will be modified.
        :param new_username: The new username of the user.
        """
        models.User.query.filter_by(username=old_username).first().username = new_username

        db.session.commit()

    @staticmethod
    def modify_voter_password(username,
                              password
                              ):
        """
        Modify user's password

        :param username: The username of the user that will be modified.
        :param password: The new password of the user.
        """
        models.User.query.filter_by(username=username).first().password = password

        db.session.commit()

    @staticmethod
    def modify_voter_section(username,
                             section_id
                             ):
        """
        Modify voter's section.

        :param username: The username of the user that will be modified.
        :param section_id: The new section of a user.
        """
        models.User.query.filter_by(username=username).first().section_id = section_id

        db.session.commit()

    @staticmethod
    def get_user(username):
        """
        Get a User object.

        :param username: The username of the user.
        """
        return models.User.query.filter_by(username=username).first()

    @staticmethod
    def get_voter_pw(username,
                     password
                     ):
        """
        Get a Voter object.

        :param username: The username of the user.
        :param password: The password of the user.
        """
        return models.User.query.filter_by(username=username,
                                           password=password
                                           ).first()

    @staticmethod
    def get_voter_count():
        """
        Get the number of voters.

        :return: An integer containing the number of voters.
        """
        return models.User.query.filter_by(role='voter').count()

    @staticmethod
    def get_section_voter_count(section_id):
        """
        Get the total number of voters of a given section.

        :param section_id: ID of the section.
        :return: Number of voters per section.
        """
        return models.User.query.filter_by(role='voter',
                                           section_id=section_id
                                           ).count()

    @staticmethod
    def is_active(username):
        """
        Check if user is active or not.

        :param username: Username of the user.
        :return: True if the user is active. False otherwise.
        """
        return models.User.query.filter_by(username=username).first().is_active()

    @staticmethod
    def set_active(username,
                   state=True
                   ):
        """
        Set the active state of a user.

        :param username: Username of the user.
        :param state: New active state of the user.
        """
        models.User.query.filter_by(username=username).first().active = state

        db.session.commit()


class VoterSection:
    """Handles the addition, deletion, and modification of voter sections."""

    @staticmethod
    def add(section_name,
            batch_id
            ):
        """
        Create a new section.

        :param section_name: Name of the section.
        :param batch_id: ID of the batch where this section is under.
        """
        db.session.add(models.VoterSection(section_name,
                                           batch_id
                                           )
                       )

        db.session.commit()

    @staticmethod
    def delete(section):
        """
        Delete a section.

        :param section: A section
        """
        models.VoterSection.query.filter_by(section_name=section).delete()

        db.session.commit()

    @staticmethod
    def delete_all():
        """
        Delete all voter sections.
        """
        models.VoterSection.query.delete()
        db.session.commit()

    @staticmethod
    def modify_section_name(old_section_name,
                            new_section_name
                            ):
        """
        Modify the name of the section

        :param old_section_name: The old name of the section.
        :param new_section_name: The new name of the section..
        """
        models.VoterSection.query.filter_by(section_name=old_section_name).first().section_name = new_section_name

        db.session.commit()

    @staticmethod
    def modify_section_batch(old_section_batch,
                             new_section_batch
                             ):
        """
        Modify the batch the section is under.

        :param old_section_batch: The old batch of a section.
        :param new_section_batch: The new batch of a section.
        """
        models.VoterSection.query.filter_by(section_name=old_section_batch).first().batch_id = new_section_batch

        db.session.commit()

    @staticmethod
    def get_voter_section(section_name):
        """
        Get a VoterSection object.

        :param section_name: The name of the section.
        :return: A VoterSection object.
        """
        return models.VoterSection.query.filter_by(section_name=section_name).first()

    @staticmethod
    def get_voter_section_by_id(section_id):
        """
        Get a VoterSection object.

        :param section_id: The table ID of the section.
        :return: A VoterSection object.
        """
        return models.VoterSection.query.filter_by(id=section_id).first()

    @staticmethod
    def get_all_voter_section_by_batch(batch_id):
        """
        Get a VoterSection object.

        :param batch_id: ID of the batch.
        :return: A VoterSection object.
        """
        return models.VoterSection.query.filter_by(batch_id=batch_id).all()

    @staticmethod
    def get_all():
        """
        Get all of the voter sections.

        :return: A list of all the sections and the corresponding ID.
        """
        return models.VoterSection.query.all()


class VoterBatch:
    """Handles the addition, deletion, and modification of the batches."""

    @staticmethod
    def add(batch_name):
        """
        Create a new batch.

        :param batch_name: The name of the new batch.
        """
        db.session.add(models.VoterBatch(batch_name))

        db.session.commit()

    @staticmethod
    def delete(batch_name):
        """
        Delete a batche.

        :param batch_name: Batch to be deleted.
        """
        models.VoterBatch.query.filter_by(batch_name=batch_name).delete()

        db.session.commit()

    @staticmethod
    def delete_all():
        """
        Delete all VoterBatch records.
        """
        models.VoterBatch.query.delete()
        db.session.commit()

    @staticmethod
    def modify_batch_name(old_batch_name,
                          new_batch_name
                          ):
        """
        Modify the current name of a batches.

        :param old_batch_name: Name of the old batch.
        :param new_batch_name: New name of the old batch.
        """
        models.VoterBatch.query.filter_by(batch_name=old_batch_name).first().batch_name = new_batch_name

        db.session.commit()

    @staticmethod
    def get_batch_by_id(id):
        """
        Get a VoterBatch object according to the ID.

        :param id: The ID of the batch.
        :return: VoterBatch object.
        """
        return models.VoterBatch.query.filter_by(id=id).first()

    @staticmethod
    def get_voter_batch(batch_name):
        """
        Get a VoterBatch object.

        :param batch_name: The name of the batch.
        :return: VoterBatch object.
        """
        return models.VoterBatch.query.filter_by(batch_name=batch_name).first()

    @staticmethod
    def get_all():
        """
        Get all of the batches.

        :return: A list of all the batches and the corresponding ID.
        """
        return models.VoterBatch.query.all()


class Candidate:
    """Handles the addition, deletion, and modification of candidates."""

    @staticmethod
    def add(first_name,
            last_name,
            middle_name,
            profile_url,
            position,
            party
            ):
        """
        Create a new candidate.

        :param first_name: First name of the candidate.
        :param last_name: Last name of the candidate.
        :param middle_name: Middle name of the candidate.
        :param profile_url: Profile link of the candidate.
        :param position: Position of the candidate.
        :param party: Party of the candidate.
        """
        db.session.add(models.Candidate(Candidate.get_next_index(),
                                        first_name,
                                        last_name,
                                        middle_name,
                                        profile_url,
                                        position,
                                        party
                                        )
                       )

        db.session.commit()

    @staticmethod
    def delete_candidate(candidate_id):
        """
        Delete a candidate.

        :param candidate_id: The ID of the candidate to be deleted.
        """
        models.Candidate.query.filter_by(id=candidate_id).first().delete()

        db.session.commit()

    @staticmethod
    def delete_all():
        """
        Delete all candidates.
        """
        models.Candidate.query.delete()
        db.session.commit()

    @staticmethod
    def modify_candidate_index(candidate_id,
                               candidate_index
                               ):
        """
        Modify the index of the candidate with respect to the position in the voting page.

        :param candidate_id: The ID of the candidate.
        :param candidate_index: The new index of the candidate.
        """
        models.Candidate.query.filter_by(id=candidate_id).first().candidate_idx = candidate_index

        db.session.commit()

    @staticmethod
    def modify_candidate_first_name(candidate_id,
                                    candidate_first_name
                                    ):
        """
        Modify the first name of the candidate.

        :param candidate_id: The ID of the candidate.
        :param candidate_first_name: The new first name of the candidate.
        """
        models.Candidate.query.filter_by(id=candidate_id).first().first_name = candidate_first_name

        db.session.commit()

    @staticmethod
    def modify_candidate_last_name(candidate_id,
                                   candidate_last_name
                                   ):
        """
        Modify the last name of the candidates.

        :param candidate_id: The ID of the candidate.
        :param candidate_last_name: The new last name of the candidate.
        """
        models.Candidate.query.filter_by(id=candidate_id).first().last_name = candidate_last_name

        db.session.commit()

    @staticmethod
    def modify_candidate_middle_name(candidate_id,
                                     candidate_middle_name
                                     ):
        """
        Modify the middle name of the candidate.

        :param candidate_id: The ID of the candidate.
        :param candidate_middle_name: The new middle name of the candidate.
        """
        models.Candidate.query.filter_by(id=candidate_id).first().middle_name = candidate_middle_name

        db.session.commit()

    @staticmethod
    def modify_candidate_position(candidate_id,
                                  candidate_position
                                  ):
        """
        Modify the position of the candidate.

        :param candidate_id: The ID of the candidate.
        :param candidate_position: The new position of the candidate.
        """
        models.Candidate.query.filter_by(id=candidate_id).first().position = candidate_position

        db.session.commit()

    @staticmethod
    def modify_candidate_party(candidate_id,
                               candidate_party
                               ):
        """
        Modify the party of the candidate.

        :param candidate_id: The ID of the candidate.
        :param candidate_party: The new party of the candidate.
        """
        models.Candidate.query.filter_by(id=candidate_id).first().party = candidate_party

        db.session.commit()

    @staticmethod
    def get_candidate(candidate_id):
        """
        Get a Candidate object.

        :param candidate_id: The ID of the candidate.
        :return: Candidate object if the Candidate exists, None otherwise.
        """
        return models.Candidate.query.filter_by(id=candidate_id).first()

    @staticmethod
    def get_candidate(candidate_position,
                      candidate_index
                      ):
        """
        Get a Candidate object based on the candidate index and position.

        :param candidate_position: The position of the candidate.
        :param candidate_index: The index of the candidate with respect to the position.
        :return: Candidate object if the candidate exists, None otherwise.
        """
        return models.Candidate.query.filter_by(position=candidate_position,
                                                candidate_idx=candidate_index
                                                ).first()

    @staticmethod
    def get_candidate_with_position(candidate_position):
        """
        Get all candidates based on the candidate position.

        :param candidate_position: Position of the candidate.
        :return: A list of all candidates of a given position.
        """
        return models.Candidate.query.filter_by(position=candidate_position).all()

    @staticmethod
    def get_profile_url(candidate_id):
        """
        Get the candidate's profile picture.

        :param candidate_id: ID of the candidate.
        :return: Return a string containing the URL of the profile picture.
        """
        return models.Candidate.query.filter_by(id=candidate_id).first()

    @staticmethod
    def get_next_index():
        """
        Get the largest candidate index and increment it by one.

        :return: The next largest candidate index.
        """
        max_index_query = db.session.query(func.max(models.Candidate.candidate_idx).label('max_index'))
        index_response = max_index_query.one()
        if index_response.max_index == 0 or index_response.max_index is None:
            return 0

        return index_response.max_index + 1

    @staticmethod
    def get_all():
        """
        Get all of the candidates.

        :return: A list of all the candidates.
        """
        return models.Candidate.query.all()


class CandidatePosition:
    """Handles the creation, deletion, and modification of candidate positions."""

    @staticmethod
    def add(position_name,
            position_level
            ):
        """
        Create a new candidate position.

        :param position_name: The name of the position.
        :param position_level: The level of the position.
        """
        db.session.add(models.CandidatePosition(name=position_name,
                                                level=position_level
                                                )
                       )

        db.session.commit()

    @staticmethod
    def delete_position(position_name):
        """
        Delete a position.

        :param position_name: The position to be deleted.
        """
        models.CandidatePosition.query.filter_by(name=position_name).first().delete()

        db.session.commit()

    @staticmethod
    def delete_all():
        """
        Delete all positions.
        """
        models.CandidatePosition.query.delete()
        db.session.commit()

    @staticmethod
    def modify_name(old_position_name,
                    new_position_name
                    ):
        """
        Modify the name of the positions.

        :param old_position_name: The old name of the position.
        :param new_position_name: The new name of the position.
        """
        models.CandidatePosition.query.filter_by(name=old_position_name).first().name = new_position_name

        db.session.commit()

    @staticmethod
    def modify_level(position_name,
                     position_level
                     ):
        """
        Modify the level of the position.

        :param position_name: The name of the position.
        :param position_level: The new level of the position.
        """
        models.CandidatePosition.query.filter_by(name=position_name).first().level = position_level

        db.session.commit()

    @staticmethod
    def get_candidate_position(position_name):
        """
        Get a CandidatePosition object.

        :param position_name: The name of the position.
        """
        return models.CandidatePosition.query.filter_by(name=position_name).first()

    @staticmethod
    def get_all():
        """
        Get all of the candidates positions.

        :return: A list of all the candidate positions.
        """
        return models.CandidatePosition.query.all()


class CandidateParty:
    """Handles the creation, deletion, and modification of the parties."""

    @staticmethod
    def add(party_name):
        """
        Create a new party.

        :param party_name: The party name.
        """
        db.session.add(models.CandidateParty(party_name))

        db.session.commit()

    @staticmethod
    def delete_party(party_name):
        """
        Delete a party.

        :param party_name: The party name to be deleted.
        """
        models.CandidateParty.query.filter_by(name=party_name).first().delete()

        db.session.commit()

    @staticmethod
    def modify_name(old_party_name,
                    new_party_name
                    ):
        """
        Modify the name of a party.

        :param old_party_name: Old party name.
        :param new_party_name: The new name of a party.
        """
        models.CandidateParty.query.filter_by(name=old_party_name).first().name = new_party_name

        db.session.commit()

    @staticmethod
    def get_candidate_party(party_name):
        """
        Get a CandidateParty object.

        :param party_name: The name of the party.
        """
        return models.CandidateParty.query.filter_by(name=party_name).first()

    @staticmethod
    def get_candidate_party_by_id(party_id):
        """
        Get a CandidateParty object by ID.

        :param party_id: The id of the party.
        :return: The CandidateParty object. Duh!
        """
        return models.CandidateParty.query.filter_by(id=party_id).first()

    @staticmethod
    def get_all():
        """
        Get all of the candidate parties.

        :return: A list of all the candidate parties.
        """
        return models.CandidateParty.query.all()


class VoteStore:
    """Handles the addition, deletion, and modification of VoteStore objects."""

    @staticmethod
    def populate():
        """
        Populate the whole VoteStore table with the current data.
        """
        candidates = Candidate.get_all()
        sections   = VoterSection.get_all()
        for candidate in candidates:
            for section in sections:
                db.session.add(models.VoteStore(section.id,
                                                candidate.id
                                                )
                               )

        db.session.commit()

    @staticmethod
    def increment_vote(candidate,
                       section
                       ):
        """
        Increment the vote of a given candidate of a section by one.

        :param candidate: The candidate whose vote will be incremented.
        :param section: The section on which the vote belongs to.
        """
        models.VoteStore.query.filter_by(candidate=candidate,
                                         voter_section=section
                                         ).first().current_votes += 1

        db.session.commit()

    @staticmethod
    def get_section_votes(section,
                          candidate
                          ):
        """
        Get the votes of a given section on a Candidate.

        :param section: The section where the votes will be gathered from.
        :param candidate: The candidate where to votes belongs to.
        :return: The section votes.
        """
        return models.VoteStore.query.filter_by(candidate=candidate,
                                                voter_section=section
                                                ).first().current_votes

    @staticmethod
    def get_candidate_total_votes(candidate):
        """
        Get the total votes of a candidate.

        :param candidate: The candidate where the votes will be gathered from.
        :return: The total votes of a given candidate.
        """
        total_votes = 0
        section_votes = models.VoteStore.query.filter_by(candidate=candidate).all()
        for section in section_votes:
            total_votes += section.current_votes

        return total_votes

    @staticmethod
    def delete_section(section):
        """
        Delete all records of a given section in the VoteStore database.

        :param section: Name of the section.
        """
        models.VoteStore.query.filter_by(section=section).delete()

        db.session.commit()

    @staticmethod
    def delete_candidate(candidate):
        """
        Delete all records of a given candidate in the VoteStore database.

        :param candidate: Name of the candidate.
        """
        models.VoteStore.query.filter_by(candidate=candidate).delete()

        db.session.commit()


class Settings:
    """Singleton class for the settings."""

    @staticmethod
    def set_property(settings_property,
                     value
                     ):
        """
        Set a property in the settings.

        :param settings_property: A property in the settings.
        :param value: The new value of the property.
        """
        logger.add_log(10,
                       'Setting property {0} to a new value: {1}.'.format(settings_property,
                                                                          value
                                                                          )
                       )
        models.SettingsModel.query.filter_by(key=settings_property).first().value = value

    @staticmethod
    def get_property_value(settings_property):
        """
        Get the value of a property.

        :param settings_property: Property in the settings.
        :return: The property value
        """
        return models.SettingsModel.query.filter_by(key=settings_property).first().value

    @staticmethod
    def property_exists(settings_property):
        """
        Check whether a property exists.

        :param settings_property: Property in the settings.
        :return: True if the property exists, False otherwise.
        """
        return models.SettingsModel.query.filter_by(key=settings_property).first() is not None

    @staticmethod
    def add_property(settings_property):
        """
        Add new settings property.

        :param settings_property: Property in the settings.
        """
        db.session.add(models.SettingsModel(settings_property,
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
        models.SettingsModel.query.filter_by(key=settings_property).delete()

        db.session.commit()