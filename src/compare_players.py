import pandas as pd

def load_rankings(csv_path="data/2025_ppr_rankings.csv"):
    return pd.read_csv(csv_path)

def find_player(df, name):
    matches = df[df['Name'].str.contains(name, case=False, na=False)]
    return matches

def compare_players(df, player1_name, player2_name):
    p1_matches = find_player(df, player1_name)
    p2_matches = find_player(df, player2_name)

    if p1_matches.empty:
        print(f"❌ No matches found for: {player1_name}")
        return
    if p2_matches.empty:
        print(f"❌ No matches found for: {player2_name}")
        return

    p1 = p1_matches.iloc[0]
    p2 = p2_matches.iloc[0]

    print("\n📊 Player Comparison:\n")
    print(f"{'Field':<15} | {p1['Name']:<25} | {p2['Name']:<25}")
    print("-" * 70)
    for field in ['Team', 'Positions', 'AvgRank', 'PosRank']:
        print(f"{field:<15} | {str(p1[field]):<25} | {str(p2[field]):<25}")

    # Recommendation
    better = p1['Name'] if p1['AvgRank'] < p2['AvgRank'] else p2['Name']
    print(f"\n✅ Recommendation: Draft **{better}** based on lower expert average rank.")

if __name__ == "__main__":
    df = load_rankings("data/positions/ALL_players.csv")  # or the full merged ranking file

    player1 = input("Enter Player 1 Name: ")
    player2 = input("Enter Player 2 Name: ")

    compare_players(df, player1, player2)
