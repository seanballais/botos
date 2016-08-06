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

from operator import itemgetter

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import SimpleDocTemplate
from reportlab.platypus import Paragraph
from reportlab.platypus import Spacer
from reportlab.platypus import Table
from reportlab.platypus import TableStyle
from reportlab.platypus import PageBreak
from reportlab.platypus.doctemplate import Indenter

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


class VotePDFGenerator:
    """Generate a PDF file of the votes."""
    pdf_link = ''

    def generate_pdf(self):
        """
        Generate a PDF file of all voting records.
        """
        content = []

        styles = getSampleStyleSheet()
        styles.add(ParagraphStyle(name='Center',
                                  alignment=TA_CENTER
                                  )
                   )

        header_text = '<font size=20>Vote Statistics</font>'
        content.append(Paragraph(header_text,
                                 styles['Center']
                                 )
                       )
        content.append(Spacer(1, 24))

        for batch in Utility.get_batch_list():
            num_voters = Utility.get_batch_voter_count(batch[0])
            batch_text = '<b>Batch {0}</b>'.format(batch[1])
            content.append(Paragraph(batch_text,
                                     styles['Center']
                                     )
                           )

            for section in Utility.get_section_of_batch_list(batch[0]):
                num_voters = controllers.User.get_section_voter_count(section.id)
                section_text = '<b><i>{0}</i></b>'.format(section.section_name)
                content.append(Paragraph(section_text,
                                         styles['Center']
                                         )
                               )

                content.append(Spacer(1, 32))

                header_rows = []
                num_voters_rows = []
                table_data = []
                header_row_count = 0
                num_voters_rows_count = 0
                for position in Utility.get_position_list():
                    header_rows.append(header_row_count)
                    total_votes = 0
                    row_count = 0
                    table_data.append(['                    ', 'Name of Candidate', 'Political Party', 'No. of Votes'])
                    for candidate in Utility.get_candidate_of_position_list(position[0]):
                        row_data = []
                        num_votes = controllers.VoteStore.get_section_votes(section.id,
                                                                            candidate['id']
                                                                            )
                        total_votes += num_votes

                        if row_count != 1:
                            row_data.append('')
                        else:
                            row_data.append(position[1])

                        candidate_name = '{0} {1}'.format(candidate['first_name'],
                                                          candidate['last_name']
                                                          )
                        row_data.append(candidate_name)
                        row_data.append(candidate['party_name'])
                        row_data.append(str(num_votes))

                        table_data.append(row_data)

                        row_count += 1
                        header_row_count += 1
                        num_voters_rows_count += 1

                    num_voters_rows_count += 1
                    num_voters_rows.append(num_voters_rows_count)

                    table_data.append(['          ', '          ', 'Total Number of Votes', str(total_votes)])
                    table_data.append(['          ', '          ', 'Abstentions', str(num_voters - total_votes)])

                    num_voters_rows_count += 2
                    header_row_count += 3

                position_table = Table(table_data)

                table_style = [
                    ('BACKGROUND', (0, 0), (0, -1), colors.Color(0.1484375, 0.1484375, 0.1484375)),
                    ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
                    ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),
                    ('BOX', (0, 0), (-1, -1), 0.25, colors.black),
                    ('INNERGRID', (0, 0), (0, -1), 0.25, colors.Color(0.1484375, 0.1484375, 0.1484375)),
                    ('TEXTCOLOR', (0, 0), (0, -1), colors.white)
                ]
                for header_row_num, num_voter_num in zip(header_rows, num_voters_rows):
                    # Modify the look of the candidate header.
                    table_style.append(
                        ('BACKGROUND', (1, header_row_num), (-1, header_row_num), colors.Color(0.496, 0.496, 0.496))
                    )
                    table_style.append(
                        ('TEXTCOLOR', (1, header_row_num), (-1, header_row_num), colors.white)
                    )
                    table_style.append(
                        ('INNERGRID', (1, header_row_num), (-1, header_row_num), 1.0, colors.Color(0.496, 0.496, 0.496))
                    )
                    table_style.append(
                        ('ALIGN', (1, header_row_num), (-1, header_row_num), 'CENTER')
                    )

                    # Modify the look of the total number of voters rows.
                    table_style.append(
                        ('BACKGROUND', (1, num_voter_num), (-2, num_voter_num), colors.Color(0.25, 0.25, 0.25))
                    )
                    table_style.append(
                        ('TEXTCOLOR', (1, num_voter_num), (-2, num_voter_num), colors.white)
                    )
                    table_style.append(
                        ('INNERGRID', (1, num_voter_num), (-2, num_voter_num), 1.0, colors.Color(0.25, 0.25, 0.25))
                    )

                    num_voter_next = num_voter_num + 1
                    table_style.append(
                        ('BACKGROUND', (1, num_voter_next), (-2, num_voter_next), colors.Color(0.25, 0.25, 0.25))
                    )
                    table_style.append(
                        ('TEXTCOLOR', (1, num_voter_next), (-2, num_voter_next), colors.white)
                    )
                    table_style.append(
                        ('INNERGRID', (1, num_voter_next), (-2, num_voter_next), 1.0, colors.Color(0.25, 0.25, 0.25))
                    )

                    # Remove the black grid in between colored cells.
                    table_style.append(
                        ('INNERGRID', (1, num_voter_num), (-2, num_voter_next), 1.0, colors.Color(0.25, 0.25, 0.25))
                    )
                    table_style.append(
                        ('BOX', (1, num_voter_num), (-2, num_voter_next), 0.25, colors.Color(0.25, 0.25, 0.25))
                    )
                    table_style.append(
                        ('BOX', (1, header_row_num), (-1, header_row_num), 0.25, colors.Color(0.496, 0.496, 0.496))
                    )
                    table_style.append(
                        ('BOX', (0, 0), (0, -1), 0.25, colors.Color(0.1484375, 0.1484375, 0.1484375))
                    )
                    table_style.append(
                        ('INNERGRID', (0, 0), (0, -1), 1.0, colors.Color(0.1484375, 0.1484375, 0.1484375))
                    )

                position_table.setStyle(TableStyle(table_style))

                content.append(position_table)
                content.append(PageBreak())

        self.document.build(content)

    def __init__(self):
        """
        Initialize the generator.
        """
        _pdf_filename = '{0}-{1}.pdf'.format(time.strftime('%Y%m%d'),
                                             time.strftime('%H%M%S')
                                             )
        self.pdf_link = 'content/xlsx/{0}'.format(_pdf_filename)
        self.filename = '{0}/{1}'.format(settings.PDF_DIRECTORY,
                                         _pdf_filename
                                         )
        self.document = SimpleDocTemplate(self.filename,
                                          pagesize=letter,
                                          rightMargin=72,
                                          leftMargin=72,
                                          topMargin=72,
                                          bottomMargin=72
                                          )


class VoterExcelGenerator:
    """Generate an Excel file of a list of voters."""
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