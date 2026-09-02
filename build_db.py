import sqlite3
import pandas as pd

excel_file = "India_Asian_Games_1951-2022_Consolidated_Medal_Winners_Final.xlsx"
df = pd.read_excel(excel_file, sheet_name="Consolidated")

# 1. Rename columns
df = df.rename(
    columns={
        "Sl No": "sl_no",
        "Edition": "edition",
        "Gold/Silver/Bronze": "medal",
        "Event": "event",
        "Sport": "sport",
        "Athletes Name": "athlete_name",
    }
)

# 2. Clean whitespace and fill missing events
df["sport"] = df["sport"].astype(str).str.strip()
df["event"] = df["event"].fillna("Unknown / Not Specified").astype(str).str.strip()
df["athlete_name"] = df["athlete_name"].astype(str).str.strip()

# 3. Consolidate sport names into standardized categories
sport_mapping = {
    "Lawn Tennis": "Tennis",
    "Lawn tennis": "Tennis",
    "Field hockey": "Field Hockey",
    "Hockey": "Field Hockey",
    "Cue sports": "Cue Sports",
    "Billiards": "Cue Sports",
    "Sepak takraw": "Sepak Takraw",
    "Table tennis": "Table Tennis",
}

df["sport"] = df["sport"].replace(sport_mapping)

# 4. Save to SQLite database
conn = sqlite3.connect("asian_games.db")
cursor = conn.cursor()

df.to_sql("medals", conn, if_exists="replace", index=False)

# Add indexes for search performance
cursor.execute("CREATE INDEX IF NOT EXISTS idx_athlete ON medals(athlete_name);")
cursor.execute("CREATE INDEX IF NOT EXISTS idx_edition ON medals(edition);")
cursor.execute("CREATE INDEX IF NOT EXISTS idx_sport ON medals(sport);")
cursor.execute("CREATE INDEX IF NOT EXISTS idx_medal ON medals(medal);")

conn.commit()
conn.close()

print(f"Success! Cleaned sports reduced from 42 to {df['sport'].nunique()} standard disciplines.")