import pandas as pd
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from sqlalchemy import create_engine
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)

# Load matches from 1990 to 2026
YEARS = range(1990, 2027)
DATA_PATH = "data/tennis_atp"

MATCH_COLUMNS = [
    'tourney_id', 'tourney_name', 'surface', 'tourney_level', 'tourney_date',
    'winner_id', 'winner_name', 'winner_hand', 'winner_age', 'winner_rank',
    'winner_rank_points', 'loser_id', 'loser_name', 'loser_hand', 'loser_age',
    'loser_rank', 'loser_rank_points', 'score', 'best_of', 'round', 'minutes',
    'w_ace', 'w_df', 'w_1stIn', 'w_1stWon', 'w_2ndWon', 'w_bpSaved', 'w_bpFaced',
    'l_ace', 'l_df', 'l_1stIn', 'l_1stWon', 'l_2ndWon', 'l_bpSaved', 'l_bpFaced'
]

def load_matches():
    all_matches = []

    for year in YEARS:
        filepath = f"{DATA_PATH}/atp_matches_{year}.csv"
        if not os.path.exists(filepath):
            print(f"Skipping {year} — file not found")
            continue

        df = pd.read_csv(filepath, usecols=lambda c: c in MATCH_COLUMNS)
        
        # Keep only columns we want
        for col in MATCH_COLUMNS:
            if col not in df.columns:
                df[col] = None

        df = df[MATCH_COLUMNS]
        all_matches.append(df)
        print(f"Loaded {year}: {len(df)} matches")

    combined = pd.concat(all_matches, ignore_index=True)
    print(f"\nTotal matches: {len(combined)}")

    combined.to_sql("matches", engine, if_exists="replace", index=True, index_label="id")
    print("Matches loaded into PostgreSQL")

def load_players():
    filepath = f"{DATA_PATH}/atp_players.csv"
    df = pd.read_csv(filepath, header=None)
    df = df.iloc[:, :6]
    df.columns = ['id', 'name_first', 'name_last', 'hand', 'dob', 'ioc']
    df.to_sql("players", engine, if_exists="replace", index=False)
    print(f"Players loaded: {len(df)}")

if __name__ == "__main__":
    load_matches()
    load_players()