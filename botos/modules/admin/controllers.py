# botos/modules/admin/controllers.py
# Copyright (C) 2016 Sean Francis N. Ballais
#
# This module is part of Botos and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php

"""Controller for the admin.

"""

import string
import random
import time

import xlsxwriter

import settings

from botos.modules.app_data import controllers
from botos.modules.activity_log import ActivityLogObservable

# Set up the logger
logger = ActivityLogObservable.ActivityLogObservable('admin_' + __name__)


class VoterGenerator:
    """Generate voters."""
    voter_list = []

    def _generate_username(self):
        """
        Generate an 8 character username.

        :return: A generated 8 character username.
        """
        username = ''
        for i in range(8):
            username += random.choice(string.digits + string.ascii_letters)

        return username

    def generate(self,
                 num_voters,
                 section_id
                 ):
        """
        Generate a list of the voters and store them in a list and the database.

        :param num_voters: Number of voters that will be generated.
        :param section_id: Section of the voters that will be generated.
        """
        alphanum_str = string.digits + string.ascii_letters
        for _ in range(num_voters):
            voter_id = ''
            password = ''
            logger.add_log(20,
                           'Generating a new voter.'
                           )

            username_exists = True
            while username_exists:
                temp_voter_id = self._generate_username()
                if controllers.User.get_user(temp_voter_id) is None:
                    voter_id = temp_voter_id
                    username_exists = False

            for i in range(16):
                password += random.choice(alphanum_str)

            logger.add_log(20,
                           'Generated voter {0}'.format(voter_id)
                           )

            controllers.User.add(voter_id,
                                 password,
                                 section_id,
                                 'voter'
                                 )
            self.voter_list.append([voter_id,
                                    password
                                    ])

    def __init__(self):
        """
        Initialize this generator.
        """
        self.voter_list = []

    def __repr__(self):
        return '<VoterGenerator>'


class VoterExcelGenerator:
    """Generate a PDF file of a list of voters."""
    xlsx_link = ''

    def generate_xlsx(self,
                      voter_list
                      ):
        """
        Generate a xlsx file with the list of voters.

        :param voter_list: List of the voters.
        """
        logger.add_log(20,
                       'Generating xlsx with {0} voters from {1}'.format(len(voter_list),
                                                                         self.section_name
                                                                         )
                       )

        header_format = self.xlsx_book.add_format()
        id_format     = self.xlsx_book.add_format()
        pass_format   = self.xlsx_book.add_format()
        header_format.set_pattern(1)
        header_format.set_bg_color('#466FC1')
        header_format.set_font_color('#FFFFFF')
        id_format.set_pattern(1)
        id_format.set_bg_color('#79A0EF')
        pass_format.set_pattern(1)
        pass_format.set_bg_color('#93ADE1')

        self.xlsx_sheet.write(0, 0, 'Voter ID', header_format)
        self.xlsx_sheet.write(0, 1, 'Password', header_format)

        row = 1
        col = 0
        for id, password in voter_list:
            self.xlsx_sheet.write(row, col, id, id_format)
            self.xlsx_sheet.write(row, col + 1, password, pass_format)
            row += 1

        self.xlsx_book.close()

    def __init__(self,
                 num_voters,
                 section_name,
                 batch
                 ):
        """
        Initialize the generator.

        :param num_voters: Number of voters.
        :param section_name: Name of the section.
        :param batch: Batch of the section.
        """
        self.section_name = section_name.section_name
        self.batch        = batch
        _xlsx_filename    = '{0}-{1}-{2}-{3}-{4}.xlsx'.format(self.batch,
                                                              self.section_name,
                                                              num_voters,
                                                              time.strftime('%Y%m%d'),
                                                              time.strftime('%H%M%S')
                                                              )
        self.xlsx_link    = 'content/xlsx/{0}'.format(_xlsx_filename)
        self.filename     = '{0}/{1}'.format(settings.XLSX_DIRECTORY,
                                             _xlsx_filename
                                             )
        self.xlsx_book    = xlsxwriter.Workbook(self.filename)
        self.xlsx_sheet   = self.xlsx_book.add_worksheet()

    def __repr__(self):
        return '<VoterPDFGenerator>'


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

    # TODO: Merge the get_x_list() functions into one.