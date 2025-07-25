# src/scraper.py
import re
import json
import requests
from bs4 import BeautifulSoup
import pandas as pd

def scrape_fantasypros_ppr():
    url = "https://www.fantasypros.com/nfl/rankings/ppr-cheatsheets.php"
    headers = {"User-Agent" : "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    html = response.text
    soup = BeautifulSoup(html, "html.parser")

    match = re.search(r'ecrData\s*=\s*(\{.*?\});', html)
    if not match:
        print("Failed to find JSON data on the page")
        return None

    data = json.loads(match.group(1))
    players = data.get('players', [])

    # save to CSV
    df = pd.DataFrame(players)

    df = df[['player_name', 'player_team_id', 'player_positions', 'rank_ave', 'pos_rank']]
    df.columns = ['Name', 'TeamID', 'Positions', 'AvgRank', 'PosRank']

    df.to_csv("data/2025_ppr_rankings.csv", index=False)
    print(f"Scraped {len(df)} players and saved to data/2025_ppr_rankings_csv")

if __name__ == "__main__":
    scrape_fantasypros_ppr()