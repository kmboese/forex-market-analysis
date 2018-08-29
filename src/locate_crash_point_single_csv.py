"""
A script that returns the date based on percent change of ask price
"""

import pandas as pd

df = pd.read_csv('GBPUSD_Ticks_2016.10.01_2016.10.31.csv', sep=",", header=[0], parse_dates=["Time (UTC)"])
df.set_index("Time (UTC)", drop=True, inplace=True)
daily_ask = df.resample("D")["Ask"]
df["daily_ask_min"] = daily_ask.transform("min")
df["daily_ask_max"] = daily_ask.transform("max")
df["daily_ask_change"] = (df["daily_ask_max"] - df["daily_ask_min"]) / df["daily_ask_max"]
print("\n")
print(df[df.daily_ask_change > 0.05]["daily_ask_change"].resample("D").mean())
