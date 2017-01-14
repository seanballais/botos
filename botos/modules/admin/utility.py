# botos/modules/admin/controllers.py
# Copyright (C) 2016 Sean Francis N. Ballais
#
# This module is part of Botos and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php

"""Controller for the admin.

"""

import settings

from operator import itemgetter

from botos.modules.app_data import controllers


class Utility:
    """Utility functions."""

    @staticmethod
    def get_batch_list():
        """
        Get a list of all batches but only including the name and ID.

        :return: List of the batches.
        """
        batch_list = []
        temp_batch_list = controllers.VoterBatch.get_all()
        for batch in temp_batch_list:
            list_batch_item = [
                batch.id,
                batch.batch_name
            ]

            batch_list.append(list_batch_item)

        batch_list.sort()
        return batch_list

    @staticmethod
    def get_section_list():
        """
        Get a list of all sections but only including the name and ID.

        :return: List of the sections.
        """
        section_list = []
        temp_section_list = controllers.VoterSection.get_all()
        for section in temp_section_list:
            list_section_item = [
                section.id,
                section.section_name
            ]

            section_list.append(list_section_item)

        section_list.sort()
        return section_list

    @staticmethod
    def get_section_of_batch_list(batch_id):
        """
        Get a list of all sections under a batch.

        :param batch_id: The ID of the batch.
        :return: List of the sections.
        """
        return controllers.VoterSection.get_all_voter_section_by_batch(batch_id)

    @staticmethod
    def get_party_list():
        """
        Get a list of all parties.

        :return: List of all parties.
        """
        party_list = []
        temp_party_list = controllers.CandidateParty.get_all()
        for party in temp_party_list:
            list_party_item = [
                party.id,
                party.name
            ]

            party_list.append(list_party_item)

        party_list.sort()
        return party_list

    @staticmethod
    def get_position_list():
        """
        Get a list of all positions.

        :return: List of all parties.
        """
        position_list = []
        temp_position_list = controllers.CandidatePosition.get_all()
        for position in temp_position_list:
            list_position_item = [
                position.id,
                position.name,
                position.level
            ]

            position_list.append(list_position_item)

        return sorted(position_list,
                      key=itemgetter(2)
                      )

    @staticmethod
    def get_candidate_of_position_list(position):
        """
        Get a list of all candidates of a given position.

        :param position: Position of the candidate.
        :return: List of the candidates of a given position.
        """
        candidate_list = []
        temp_candidate_list = controllers.Candidate.get_candidate_with_position(position)
        for candidate in temp_candidate_list:
            list_candidate_item = {
                'id': candidate.id,
                'first_name': candidate.first_name,
                'last_name': candidate.last_name,
                'profile_url': candidate.profile_url,
                'party_name': controllers.CandidateParty.get_candidate_party_by_id(candidate.party).name
            }

            candidate_list.append(list_candidate_item)

        return sorted(candidate_list,
                      key=lambda k: k['id']
                      )

    @staticmethod
    def get_batch_voter_count(batch_id):
        """
        Get the total number of voters of a given batch.

        :param batch_id: ID of the batch.
        :return: Number of voters per batch.
        """
        num_voters = 0
        for section in Utility.get_section_of_batch_list(batch_id):
            num_voters += controllers.User.get_section_voter_count(section.id)

        return num_voters

    @staticmethod
    def file_extensions_allowed(extension):
        """
        Check if the file extension is allowed.

        :param extension: File extension.
        :return: Return True if allowed. False, otherwise.
        """
        return extension in settings.ALLOWED_EXTENSIONS

    @staticmethod
    def get_file_extension(filename):
        """
        Get the file extension.

        :param filename: Filename where we will get the file extension.
        :return: Return the file extension. Return '' if none.
        """
        if '.' in filename:
            return filename.rsplit('.', 1)[1]

        return ''

    # TODO: Merge the get_x_list() functions into one.