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

from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import SimpleDocTemplate
from reportlab.platypus import Paragraph
from reportlab.platypus import Spacer

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


class VoterPDFGenerator:
    """Generate a PDF file of a list of voters."""
    filename = ''

    def generate_entry_pdf(self,
                           voter_list
                           ):
        """
        Generate a PDF with the list of voters. This document will be used before entry to
        the voting station. Before entry, the voter must sign the voter ID he/she will be using
        for voting.

        :param voter_list: List of the voters.
        """
        contents = []
        styles = getSampleStyleSheet()

        styles.add(ParagraphStyle(name='Center',
                                  alignment=TA_CENTER
                                  )
                   )
        text = '<font size=16><bold>Voter Personal Access Information</bold></font><br/>'
        text += '<font size=12>Section: {0}</font>'.format(self.section_name)

        contents.append(Paragraph(text,
                                  styles['Center']
                                  )
                        )
        contents.append(Spacer(1, 14))

        # Create the list.
        text = '<font size=12><bold>                  Voter ID   Password</bold></font>'
        contents.append(Paragraph(text,
                                  styles['Center']
                                  )
                        )
        contents.append(Spacer(1, 12))
        for voter in voter_list:
            text = '<font size=12>_______________   {0}   {1}<br/>'.format(voter[0],  # Voter ID
                                                                           voter[1]   # Password
                                                                           )
            contents.append(Paragraph(text,
                                      styles['Center']
                                      )
                            )

        contents.append(Spacer(1, 24))
        contents.append(Paragraph('<font size=12><i>{0}</i></font>'.format(settings.election_closing_text),
                                  styles['Center']
                                  )
                        )
        contents.append(Spacer(1, 32))

        text = '<font size=12><b>Powered by Botos</b><br/>'
        text += '<small>Botos is an open source election system developed by Sean Francis N. Ballais.</small></font>'
        contents.append(Paragraph(text,
                                  styles['Center']
                                  )
                        )
        self.pdf_doc.build(contents)

    def __init__(self,
                 num_voters,
                 section_name
                 ):
        """
        Initialize the generator.

        :param num_voters: Number of voters.
        :param section_name: Name of the section.
        """
        self.filename     = '{0}/{1}-{2}-{3}-{4}-{5}.pdf'.format(settings.PDF_DIRECTORY,
                                                                 section_name,
                                                                 num_voters,
                                                                 section_name,
                                                                 time.strftime('%Y%m%d'),
                                                                 time.strftime('%H%M%S')
                                                                 )
        self.pdf_doc      = SimpleDocTemplate(filename=self.filename,
                                              pagesize=letter,
                                              rightMargin=72,
                                              leftMargin=72,
                                              topMargin=72,
                                              bottomMargin=72
                                              )
        self.section_name = section_name

    def __repr__(self):
        return '<VoterPDFGenerator>'