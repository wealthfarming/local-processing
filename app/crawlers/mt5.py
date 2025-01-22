from .base import DataSource

class MT5DataSource(DataSource):
    def connect(self):
        print("Connecting to MT5 server...")

    def pull_data(self):
        print("Pulling raw data from MT5...")
        return {"raw": "MT5 data"}

    def clean_data(self, raw_data):
        print("Cleaning MT5 data...")
        return {"cleaned": raw_data["raw"].upper()}

    def close_connection(self):
        print("Closing connection to MT5 server.")
