# botos/modules/admin/controllers.py
# Copyright (C) 2016 Sean Francis N. Ballais
#
# This module is part of Botos and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php

"""Controller for the admin.

"""

import time

import settings

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

from botos.modules.app_data import controllers
from botos.modules.admin.utility import Utility
from botos.modules.activity_log import ActivityLogObservable

# Set up the logger
logger = ActivityLogObservable.ActivityLogObservable('admin_' + __name__)


class VoterGenerator:
    """Generate voters."""
    voter_list = []

    @staticmethod
    def generate(voter_sheet, section_id):
        """
        Generate a list of the voters from an Excel worksheet and store them to the database.
        The format of the Excel worksheet must be:

        ------------------|------------------
        | Header title                      |  <- This can have any title.
        |-----------------|-----------------|
        |  ID             |  Password       |  <- Not necessarily worded like this but the
        |-----------------|-----------------|     order of the columns must be as shown.
        |  11-08-008      |  ABC123         |
        |  ...            |  ...            |
        |-----------------|-----------------|

        :param voter_sheet: The sheet in the XLSX file containing the voter ID and password.
        :param section_id: ID of the section where the voters belong to.
        """
        for row in range(3, voter_sheet.max_row + 1):
            # Note that voter_sheet.max_row starts counting from 0.
            voter_id = voter_sheet.cell(row=row, column=1).value
            password = voter_sheet.cell(row=row, column=2).value

            logger.add_log(20, 'Creating new voter with an ID of {0}.'.format(voter_id))

            if controllers.User.get_user(voter_id) is None:
                controllers.User.add(voter_id, password, section_id, 'voter')
            else:
                logger.add_log(20, 'Voter \'{0}\' is already in the database. Skipping creation.'.format(voter_id))

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