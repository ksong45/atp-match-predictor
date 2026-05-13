from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Match(Base):
    __tablename__ = "matches"

    id = Column(Integer, primary_key=True, index=True)
    tourney_id = Column(String)
    tourney_name = Column(String)
    surface = Column(String)
    tourney_level = Column(String)
    tourney_date = Column(String)
    winner_id = Column(Integer)
    winner_name = Column(String)
    winner_hand = Column(String)
    winner_age = Column(Float)
    winner_rank = Column(Integer)
    winner_rank_points = Column(Integer)
    loser_id = Column(Integer)
    loser_name = Column(String)
    loser_hand = Column(String)
    loser_age = Column(Float)
    loser_rank = Column(Integer)
    loser_rank_points = Column(Integer)
    score = Column(String)
    best_of = Column(Integer)
    round = Column(String)
    minutes = Column(Float)
    w_ace = Column(Float)
    w_df = Column(Float)
    w_1stIn = Column(Float)
    w_1stWon = Column(Float)
    w_2ndWon = Column(Float)
    w_bpSaved = Column(Float)
    w_bpFaced = Column(Float)
    l_ace = Column(Float)
    l_df = Column(Float)
    l_1stIn = Column(Float)
    l_1stWon = Column(Float)
    l_2ndWon = Column(Float)
    l_bpSaved = Column(Float)
    l_bpFaced = Column(Float)

class Player(Base):
    __tablename__ = "players"

    id = Column(Integer, primary_key=True)
    name_first = Column(String)
    name_last = Column(String)
    hand = Column(String)
    dob = Column(String)
    ioc = Column(String)