import botos
from botos.modules.api.models import Base


class Voter(Base):
    """The Voter class represents voters using this system."""
    __tablename__ = 'voter'
    id            = botos.db.Column(botos.db.String(8),
                                    nullable=False,
                                    unique=True
                                    )
    password      = botos.db.Column(botos.db.String(128),
                                    nullable=False
                                    )
    section       = botos.db.Column(botos.db.String())
