"""
Models here will be used by the entire application.

Using a application-wide database handler to avoid duplication of
data and cumbersome coding.
"""
from app import db
from botos.modules.api.models import Base


class VoterKeys(Base):
    """The class in which the voters' information will be derived from."""

    __tablename__ = 'voter_keys'
    voter_group   = ''  # Must be a foreign key
