# -*- coding: utf-8 -*-
"""visualChartDataPreparation.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1T8i5oY_CeGGAPEGjGVr6O90hxD0FqgVp
"""
import pandas as pd
import numpy as np

df = pd.read_csv(r"C:\Users\malfo\Google Drive\python\TFM\dax1992min.csv", usecols=(
    "<DTYYYYMMDD>", "<TIME>", "<OPEN>", "<HIGH>", "<LOW>", "<CLOSE>"))
df.columns = ["date", "time", "open", "high", "low", "close"]
df["time"] = df["time"] / 100

# we delete every period before 9 PM
df = df.loc[df["time"] > 900]

# we drop every day that has less than 600 minutes (days when close is early)
mask = df.groupby("date").count()["time"] < 600
mask = mask.reset_index().replace(False, np.NaN).dropna()
for day in list(mask.date):
    df.loc[df["date"] == day] = np.NaN
df=df.dropna().reset_index()

df.to_csv("dax_cleaned.csv")

# opening of the first period of the day and thus, opening of the day
dOpen = df.groupby("date").first().open

# close of the last period of the day, and thus, close of the day
dClose = df.groupby("date").last().close

# max of the day
dMax = df.groupby("date").max().high

# min of the day
dMin = df.groupby("date").min().low

# list of the days
days = df.groupby("date").min()
days = days.reset_index().date.to_frame()
print("dataset has " + str(df["time"].size) + " periods of one minute and " + str(days.size) + " days")

# we get the hinge for each day, being the hinge the minimum between the
# diference between the oppening and the max and the difference between 
# the difference and the min
lowerHinges = dOpen.to_numpy() - dMin.to_numpy()
upperHinges = dOpen.to_numpy() - dMax.to_numpy()
hinges = np.minimum(abs(upperHinges), abs(lowerHinges))
meanHinges = np.mean(hinges)
stdHinges = np.std(hinges)

# last20Hinges contains, for each day of our database, the hinges of the 
# previous N (20) days (N entries per day)
N = 20
last20Hinges = np.zeros((days.shape[0], N))
for x in range(last20Hinges.shape[1]):
    last20Hinges[:, x] = np.pad(hinges, (x + 1, 0), mode="constant")[0:days.shape[0]]

# means and std contain for each day of the database, the mean and std of 
# the hinges of the last 20 days (1 entry per day)
means = np.mean(last20Hinges, axis=1)
std = np.std(last20Hinges, axis=1)

# the stretch is the mean + 4 times the std (1 entry per day)
stretches = means + 4 * std

# dict is a dictionary that contains for each day, its opening and its stretch
dict = {'date': days.to_numpy().flatten().tolist(),
        "open": dOpen.to_list(), 'stretch': stretches.tolist()}
dfDaily = pd.DataFrame(dict)

# for each day, we compute top and bottom limits as the close of th
dfDaily["upper limit"] = dfDaily.open + dfDaily.stretch
dfDaily["bottom limit"] = dfDaily.open - dfDaily.stretch

# we place the bottom and upper limits, but it will only place values on the 
# first period of each day. 
N = 500
df2 = df.copy()
df2.loc[df["date"].drop_duplicates().index, "upper limit"] = dfDaily["upper limit"].to_numpy()
df2.loc[df["date"].drop_duplicates().index, "bottom limit"] = dfDaily["bottom limit"].to_numpy()

# If none of the limits is breaken on the first N minutes, both limits are set 
# to be the openning of the day
df2.loc[df["date"].drop_duplicates().index + N, "bottom limit"] = dfDaily["open"].to_numpy()
df2.loc[df["date"].drop_duplicates().index + N, "upper limit"] = dfDaily["open"].to_numpy()

# we fill the missing values using the last valid value
df2 = df2.fillna(method='ffill')

# we create 2 columns that indicates wheter the close of a given period is above
# the upper limit of the day or bellow the bottom limit of the day
df2["breaks top"] = df2["close"] > df2["upper limit"]
df2["breaks bottom"] = df2["close"] < df2["bottom limit"]

# first we take the columns "breaks top" and "date" and repace False values with
# NaN values. We do this because of how .idxmax() works. Then we group by date
# and use .idxmax() that returns for each column of grouped data, the index of
# the first not null value. Finally, we extract the "breaks top column", that
# will contain, for each day, the index of the first True value, e.g. the index 
# of the first minute that ends above the top limit. 
# The process is repeated for the bottom limit
topBreakings = df2[['breaks top', "date"]].replace(False, np.NaN).groupby("date").idxmax()["breaks top"].replace(np.NaN,
                                                                                                                 99999999)
bottomBreakings = df2[['breaks bottom', "date"]].replace(False, np.NaN).groupby("date").idxmax()[
    "breaks bottom"].replace(np.NaN, 99999999)

# we finally compute if the day will be bullish (alcista) or bearish (bajista)
# by looking what breaking happens earlier.
dfDaily["bullish"] = np.int32(topBreakings < bottomBreakings)
print("there are" + str(sum(dfDaily["bullish"])) + " up days and " + str(
    dfDaily["bullish"].size - sum(dfDaily["bullish"]))
      + " down days")

frame = {'first top breaking index': topBreakings,
         'first bottom breaking index': bottomBreakings,
         "bullish": topBreakings < bottomBreakings
         }
pd.DataFrame(frame)

dict = {'date': days.to_numpy().flatten().tolist(), "open": dOpen.to_list(),
        "close": dClose.to_list(), "min": dMin.to_list(), "max": dMax.to_list(),
        "bullish": dfDaily["bullish"].to_list()}
dfMl = pd.DataFrame(dict).dropna()
dfMl.to_csv("dfMl.csv")
