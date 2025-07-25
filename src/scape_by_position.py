import re
import json
import requests
import pandas as pd
from bs4 import BeautifulSoup
from collections import defaultdict
import os

def scrape_fantasypros_format(page_slug):
    url = f"https://www.fantasypros.com/nfl/rankings/{page_slug}.php"
    headers = {"User-Agent": "Mozilla/5.0"}
    resp = requests.get(url, headers=headers)
    html = resp.text
    soup = BeautifulSoup(html, 'html.parser')

    # Look for JSON data in JavaScript
    match = re.search(r'ecrData\s*=\s*(\{.*?\});', html)
    if not match:
        print("❌ Failed to find player JSON on the page.")
        return None

    data = json.loads(match.group(1))
    players = data.get('players', [])

    if not players:
        print("⚠️ No players found in the JSON data.")
        return None

    df = pd.DataFrame(players)
    df = df[['player_name', 'player_team_id', 'player_positions', 'rank_ave', 'pos_rank']]
    df.columns = ['Name', 'Team', 'Positions', 'AvgRank', 'PosRank']
    return df

def split_by_position(df):
    position_dfs = defaultdict(list)

    for _, row in df.iterrows():
        positions = row['Positions']
        if isinstance(positions, list):  # In case player has multiple positions
            for pos in positions:
                position_dfs[pos].append(row)
        else:
            position_dfs[positions].append(row)

    return {pos: pd.DataFrame(rows) for pos, rows in position_dfs.items()}

def save_to_csv_by_position(position_dfs, folder="data/positions"):
    os.makedirs(folder, exist_ok=True)
    for pos, df in position_dfs.items():
        path = os.path.join(folder, f"{pos}_players.csv")
        df.to_csv(path, index=False)
        print(f"✅ Saved {len(df)} {pos} players to {path}")

if __name__ == "__main__":
    rankings_page = "dynasty-overall"  # You can change this to ppr-cheatsheets or other slugs
    df = scrape_fantasypros_format(rankings_page)

    if df is not None:
        position_dfs = split_by_position(df)
        save_to_csv_by_position(position_dfs)
