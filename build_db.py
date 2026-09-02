import sqlite3
import pandas as pd

# 1. Load Excel dataset from the "Consolidated" sheet
excel_file = "India_Asian_Games_1951-2022_Consolidated_Medal_Winners_Final.xlsx"
df = pd.read_excel(excel_file, sheet_name="Consolidated")

# 2. Clean and standardize column names
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
df["event"] = df["event"].fillna("Unknown / Not Specified")
df["athlete_name"] = df["athlete_name"].astype(str).str.strip()

# 3. Create and populate the SQLite database
conn = sqlite3.connect("asian_games.db")
cursor = conn.cursor()

df.to_sql("medals", conn, if_exists="replace", index=False)

# 4. Add query performance indexes
cursor.execute("CREATE INDEX IF NOT EXISTS idx_athlete ON medals(athlete_name);")
cursor.execute("CREATE INDEX IF NOT EXISTS idx_edition ON medals(edition);")
cursor.execute("CREATE INDEX IF NOT EXISTS idx_sport ON medals(sport);")
cursor.execute("CREATE INDEX IF NOT EXISTS idx_medal ON medals(medal);")

conn.commit()
conn.close()
print("Success: 'asian_games.db' has been created.")