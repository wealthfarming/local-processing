import sys

sys.path.append("app")
from crawlers.mt5 import MT5DataSource

# Initialize the MT5DataSource
mt5_source = MT5DataSource()

try:
    # Step 1: Connect to the MT5 server
    mt5_source.connect()

    # Step 2: Pull data
    raw_data = mt5_source.pull_data()
    print("Raw data:", raw_data)

    # Step 3: Clean data
    cleaned_data = mt5_source.clean_data(raw_data)
    print("Cleaned data:", cleaned_data)

finally:
    # Step 4: Close the connection
    mt5_source.close_connection()
