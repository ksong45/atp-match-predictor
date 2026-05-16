import pandas as pd
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import os

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)

def get_surface_win_rate(player_name, surface, months_back=24):
    query = text("""
        SELECT 
            COUNT(CASE WHEN winner_name = :player THEN 1 END) as wins,
            COUNT(*) as total
        FROM matches
        WHERE (winner_name = :player OR loser_name = :player)
        AND surface = :surface
        AND CAST(tourney_date AS TEXT) >= :cutoff_date
    """)
    
    from datetime import datetime, timedelta
    cutoff = (datetime.now() - timedelta(days=months_back * 30)).strftime('%Y%m%d')
    
    with engine.connect() as conn:
        result = conn.execute(query, {
            "player": player_name,
            "surface": surface,
            "cutoff_date": cutoff
        }).fetchone()
    
    if result and result.total > 0:
        return round(result.wins / result.total, 3)
    return 0.5  # default if no data

def get_recent_form(player_name, last_n=15):
    """Win rate over last N matches regardless of surface"""
    query = text("""
        SELECT winner_name
        FROM (
            SELECT winner_name, tourney_date
            FROM matches
            WHERE winner_name = :player OR loser_name = :player
            ORDER BY tourney_date DESC
            LIMIT :n
        ) recent
    """)
    
    with engine.connect() as conn:
        results = conn.execute(query, {
            "player": player_name,
            "n": last_n
        }).fetchall()
    
    if not results:
        return 0.5
    
    wins = sum(1 for r in results if r.winner_name == player_name)
    return round(wins / len(results), 3)

def get_h2h(player1, player2, surface=None):
    """Head to head record, optionally filtered by surface"""
    if surface:
        query = text("""
            SELECT
                COUNT(CASE WHEN winner_name = :p1 THEN 1 END) as p1_wins,
                COUNT(CASE WHEN winner_name = :p2 THEN 1 END) as p2_wins
            FROM matches
            WHERE ((winner_name = :p1 AND loser_name = :p2)
                OR (winner_name = :p2 AND loser_name = :p1))
            AND surface = :surface
        """)
        params = {"p1": player1, "p2": player2, "surface": surface}
    else:
        query = text("""
            SELECT
                COUNT(CASE WHEN winner_name = :p1 THEN 1 END) as p1_wins,
                COUNT(CASE WHEN winner_name = :p2 THEN 1 END) as p2_wins
            FROM matches
            WHERE (winner_name = :p1 AND loser_name = :p2)
                OR (winner_name = :p2 AND loser_name = :p1)
        """)
        params = {"p1": player1, "p2": player2}

    with engine.connect() as conn:
        result = conn.execute(query, params).fetchone()

    total = result.p1_wins + result.p2_wins
    if total == 0:
        return 0.5
    return round(result.p1_wins / total, 3)

def get_ranking_trajectory(player_name):
    """Compare current rank to rank 3 months ago — positive means improving"""
    query = text("""
        SELECT winner_rank as rank, tourney_date
        FROM matches
        WHERE winner_name = :player AND winner_rank IS NOT NULL
        UNION
        SELECT loser_rank as rank, tourney_date
        FROM matches
        WHERE loser_name = :player AND loser_rank IS NOT NULL
        ORDER BY tourney_date DESC
        LIMIT 20
    """)

    with engine.connect() as conn:
        results = conn.execute(query, {"player": player_name}).fetchall()

    if len(results) < 2:
        return 0

    current_rank = results[0].rank
    old_rank = results[-1].rank
    # Positive = improving (rank number went down)
    return old_rank - current_rank

def get_tournament_win_rate(player_name, tourney_name):
    """Historical win rate at a specific tournament"""
    query = text("""
        SELECT
            COUNT(CASE WHEN winner_name = :player THEN 1 END) as wins,
            COUNT(*) as total
        FROM matches
        WHERE (winner_name = :player OR loser_name = :player)
        AND tourney_name = :tourney
    """)

    with engine.connect() as conn:
        result = conn.execute(query, {
            "player": player_name,
            "tourney": tourney_name
        }).fetchone()

    if result and result.total > 0:
        return round(result.wins / result.total, 3)
    return 0.5

def get_current_rank(player_name):
    """Get player's most recent ranking"""
    query = text("""
        SELECT winner_rank as rank, tourney_date
        FROM matches
        WHERE winner_name = :player AND winner_rank IS NOT NULL
        UNION
        SELECT loser_rank as rank, tourney_date
        FROM matches
        WHERE loser_name = :player AND loser_rank IS NOT NULL
        ORDER BY tourney_date DESC
        LIMIT 1
    """)

    with engine.connect() as conn:
        result = conn.execute(query, {"player": player_name}).fetchone()

    return result.rank if result else 999

def get_player_elo(player_name):
    """Get player's current Elo rating from database"""
    query = text("""
        SELECT elo FROM player_elo
        WHERE LOWER(player_name) = LOWER(:player)
        LIMIT 1
    """)
    with engine.connect() as conn:
        result = conn.execute(query, {"player": player_name}).fetchone()
    return float(result.elo) if result else 1500.0

def get_player_age(player_name):
    """Get player age from players table via DOB"""
    query = text("""
        SELECT dob FROM players
        WHERE CONCAT(name_first, ' ', name_last) = :player
        LIMIT 1
    """)
    with engine.connect() as conn:
        result = conn.execute(query, {"player": player_name}).fetchone()
    
    if result and result.dob:
        try:
            from datetime import datetime
            dob = str(result.dob)
            birth = datetime.strptime(dob, "%Y%m%d")
            age = (datetime.now() - birth).days / 365.25
            return round(age, 1)
        except:
            return 25.0
    return 25.0

def compute_features(player1, player2, surface, tourney_name, round):
    print(f"Computing features for {player1} vs {player2} on {surface}...")

    p1_rank = get_current_rank(player1)
    p2_rank = get_current_rank(player2)

    features = {
        # Player 1
        "p1_surface_wr":  get_surface_win_rate(player1, surface),
        "p1_recent_form": get_recent_form(player1),
        "p1_rank":        p1_rank,
        "p1_elo":         get_player_elo(player1),
        "p1_age":         get_player_age(player1),
        "p1_ace_rate":    0.0,
        "p1_1st_serve":   0.0,
        "p1_1st_won":     0.0,
        "p1_bp_saved":    0.0,
        # Player 2
        "p2_surface_wr":  get_surface_win_rate(player2, surface),
        "p2_recent_form": get_recent_form(player2),
        "p2_rank":        p2_rank,
        "p2_elo":         get_player_elo(player2),
        "p2_age":         get_player_age(player2),
        "p2_ace_rate":    0.0,
        "p2_1st_serve":   0.0,
        "p2_1st_won":     0.0,
        "p2_bp_saved":    0.0,
        # H2H
        "h2h":            get_h2h(player1, player2, surface),
        # Differentials
        "rank_diff":      p2_rank - p1_rank,
        "elo_diff":       get_player_elo(player1) - get_player_elo(player2),
        "age_diff":       0.0,
        # Match context
        "surface_clay":   1 if surface == "Clay" else 0,
        "surface_grass":  1 if surface == "Grass" else 0,
        "surface_hard":   1 if surface == "Hard" else 0,
        "is_grand_slam":  1 if tourney_name in [
                            "Australian Open", "Roland Garros",
                            "Wimbledon", "US Open"] else 0,
        "round_num":      {"F": 7, "SF": 6, "QF": 5, "R16": 4,
                           "R32": 3, "R64": 2, "R128": 1}.get(round, 3),
        "best_of":        5 if tourney_name in [
                            "Australian Open", "Roland Garros",
                            "Wimbledon", "US Open"] else 3,
    }

    return features

if __name__ == "__main__":
    # Quick test
    features = compute_features(
        "Carlos Alcaraz", "Jannik Sinner",
        "Clay", "Roland Garros", "F"
    )
    for key, value in features.items():
        print(f"{key}: {value}")