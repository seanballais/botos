from botos import db


class Base(db.Model):
    """The Base class is the class where all classes will inherit from."""
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
