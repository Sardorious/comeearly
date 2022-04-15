# from datetime import datetime as dt

import pandas as pd

from draw import plot_reg, plot_timeseries

df = pd.read_csv("./sheet.csv")

df["datetime"] = pd.to_datetime(df["date"], format="%Y-%m-%d")

df = df[(df["check_type"] == "in") & (df["datetime"].dt.month == 4)]

plot_timeseries(df, "April", False)

plot_reg(df, "April", False)
