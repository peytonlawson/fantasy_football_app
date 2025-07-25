import streamlit as st
import pandas as pd
import difflib

# Load data
@st.cache_data
def load_player_data(path="data/2025_ppr_rankings.csv"):
    df = pd.read_csv(path)
    df = df.rename(columns={
        'player_team_id': 'TeamID',
        'player_positions': 'Positions',
        'rank_ave': 'AvgRank',
        'pos_rank': 'PosRank'
    })
    df['Name'] = df['Name'].astype(str)
    return df

df = load_player_data()

# Get all available positions
all_positions = set()
for val in df['Positions']:
    if isinstance(val, str):
        if val.startswith("["):  # stringified list like "['WR']"
            try:
                val = eval(val)
            except Exception:
                val = [val]
        if isinstance(val, list):
            all_positions.update(val)
        else:
            all_positions.add(val)

# Add "All" to the filter options
sorted_positions = ["All"] + sorted(list(all_positions))

# Streamlit UI
st.title("🏈 Fantasy Football Player Comparison Tool")
st.markdown("Use the position filter and search boxes to compare two players by expert rank.")

# Position filter (only affects dropdown suggestions)
selected_pos = st.selectbox("🔍 Filter dropdowns by Position", sorted_positions)

# Player name pool based on filter
if selected_pos == "All":
    name_pool = df['Name'].unique()
else:
    name_pool = df[df['Positions'].apply(lambda x: selected_pos in str(x))]['Name'].unique()

# Smart fuzzy match
def fuzzy_match_options(query, options, limit=10):
    return difflib.get_close_matches(query, options, n=limit, cutoff=0.1)

# Player search inputs
st.markdown("### ✏️ Type a name to search")
player1_query = st.text_input("Player 1 Name", "")
player2_query = st.text_input("Player 2 Name", "")

# Fuzzy match results
player1_matches = fuzzy_match_options(player1_query, name_pool)
player2_matches = fuzzy_match_options(player2_query, name_pool)

# Select from fuzzy matches
player1 = st.selectbox("Select Player 1", player1_matches) if player1_matches else None
player2 = st.selectbox("Select Player 2", player2_matches) if player2_matches else None

# Fetch full data (from unfiltered DataFrame)
def get_player_data(name):
    row = df[df['Name'] == name]
    return row.iloc[0] if not row.empty else None

# Comparison logic
if player1 and player2:
    p1 = get_player_data(player1)
    p2 = get_player_data(player2)

    if p1 is not None and p2 is not None:
        st.subheader("📊 Player Comparison")

        comparison_df = pd.DataFrame({
            "Field": ["TeamID", "Position(s)", "Avg Expert Rank", "Position Rank"],
            player1: [p1['TeamID'], p1['Positions'], p1['AvgRank'], p1['PosRank']],
            player2: [p2['TeamID'], p2['Positions'], p2['AvgRank'], p2['PosRank']]
        })

        st.dataframe(comparison_df.set_index("Field"))

        better = player1 if p1['AvgRank'] < p2['AvgRank'] else player2
        st.success(f"✅ **Recommendation**: Draft **{better}** based on expert average rank.")
    else:
        st.warning("Could not load player details.")
else:
    st.info("Start typing a name above to compare players.")
