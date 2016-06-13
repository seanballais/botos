from botos import db


class Base(db.Model):
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


class Voter(Base):
    __tablename__ = 'voter'
    voter_id      = db.Column(db.String(8),
                              nullable=False,
                              unique=True
                              )
    password      = db.Column(db.String(128),
                              nullable=False
                              )
    voter_section = db.Column()  # ForeignKey


class VoterSection(Base):
    __tablename__ = 'voter_section'
    section_name  = db.Column(db.String(16),
                              nullable=False,
                              unique=True
                              )
    section_votes = db.Column(db.Integer)
    section_batch = db.Column(db.String(4),
                              
                              )


class VoterBatch(Base):
    __tablename__ = 'voter_batch'
    batch_year    = db.Column(db.String,
                              nullable=False,
                              unique=True
                              )


class CandidatePosition(Base):
    __tablename__  = 'candidate_position'
    name           = db.Column(db.String(32),
                               nullable=False,
                               unique=True
                               )
    level          = db.Column(db.SmallInteger,
                               nullable=False
                               )


class Candidate(Base):
    __tablename__   = 'candidate'
    first_name      = db.Column(db.String(16),
                                nullable=False
                                 )
    last_name       = db.Column(db.String(16),
                                nullable=False
                                )
    middle_name     = db.Column(db.String(16),
                                nullable=True
                                )
    position        = db.Column()  # ForeignKey
    party           = db.Column()  # ForeignKey
    candidate_index = db.Column(db.SmallInteger,
                                nullable=False
                                )