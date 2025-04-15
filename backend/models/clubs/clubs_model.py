from sqlalchemy import Boolean, Column, String, JSON, ForeignKey, Table
from sqlalchemy.orm import relationship

from utils.database_utils import Base

# association table for many-to-many relationship between users and clubs
club_members = Table('club_members', Base.metadata, Column('club_id', String, ForeignKey('clubs.cid')),
                     Column('user_id', String, ForeignKey('users.uid')), Column('role', String),
                     Column('is_poc', Boolean, default=False))


class Club(Base):
    __tablename__ = "clubs"

    cid = Column(String, unique=True, nullable=False, primary_key=True)  # Club ID from Clubs Council
    name = Column(String, nullable=False)
    tagline = Column(String, nullable=True)
    description = Column(String, nullable=True)
    category = Column(String, nullable=True)
    code = Column(String, nullable=True)
    logo = Column(String, nullable=True)
    banner = Column(String, nullable=True)
    banner_square = Column(String, nullable=True)
    state = Column(String, nullable=True)
    email = Column(String, nullable=True)
    socials = Column(JSON, nullable=True)

    # many-to-many relationship with users
    members = relationship("User", secondary=club_members, backref="clubs")
