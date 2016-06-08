"""
Models here will be used by the entire application.

Using a application-wide database handler to avoid duplication of
data and cumbersome coding.
"""
from botos import db


class Base(db.Model):
    """The base model from which other models will inherit from."""

    __abstract__  = True

    id            = db.Column(db.Integer,
                              primary_key=True
                              )
    date_created  = db.Column(db.DateTime,
                              default=db.func.current_timestamp()
                              )
    date_modified = db.Column(db.DateTime,
                              default=db.func.current_timestamp(),
                              onupdate=db.func.current_timestamp()
                              )
