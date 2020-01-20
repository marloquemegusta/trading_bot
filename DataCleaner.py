# requires numpy and pandas to work
def DataCleaner(path, std=1, return_full_dataFrame=False):
    import pandas as pd
    import numpy as np
    df = pd.read_csv(path, usecols=(
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
    df = df.dropna().reset_index(drop=True)
    dfCleaned = df.copy()
    # opening of the first period of the day and thus, opening of the day
    dOpen = df.groupby("date").first().open.values
    print(str(dOpen.size) + " days loaded")

    # close of the last period of the day, and thus, close of the day
    dClose = df.groupby("date").last().close.values

    # max of the day
    dMax = df.groupby("date").max().high.values

    # min of the day
    dMin = df.groupby("date").min().low.values

    # list of the days
    days = df.groupby("date").min()
    days = days.reset_index().date.to_frame()

    # we get the hinge for each day, being the hinge the minimum between the
    # openning-maximum spread and the openning-minimum spread
    lowerHinges = dOpen - dMin
    upperHinges = dOpen - dMax
    hinges = np.minimum(abs(upperHinges), abs(lowerHinges))
    hingesdf = pd.DataFrame(hinges)

    numDays = 20

    # stretch for each day is the mean+std of the previous 20 days
    window = hingesdf.rolling(numDays, min_periods=1)
    stretches = (window.mean() + std * window.std()).values.flatten()  # 1 stretch per day

    # dayIndex contains the index of the first period of each day in df
    dayIndex = df["date"].drop_duplicates().index
    df2 = df.copy()

    # we initialize new columns
    df2["upper limit"] = np.NaN
    df2["bottom limit"] = np.NaN
    df2["stretch"] = np.NaN

    # we place the stretch and limits (open of the day +- stretch) on the first
    # period of each day

    df2.loc[dayIndex, "stretch"] = stretches
    df2.loc[dayIndex, "upper limit"] = (dOpen + stretches)
    df2.loc[dayIndex, "bottom limit"] = (dOpen - stretches)

    # we place both limits at the openning of the day at minute N(500 in this case)
    N = 500
    df2.loc[dayIndex + N, "upper limit"] = dOpen
    df2.loc[dayIndex + N, "bottom limit"] = dOpen

    # finally, we perform a forward fill  by filling all NaN value with the last
    # valid value
    df2 = df2.fillna(method='ffill')
    # for each period (minutes in this case) we define a flag to indicate wheter
    # it ends up above upper limit or bellow bottom limit
    df2["breaks upper limit"] = df2["close"] > df2["upper limit"]
    df2["breaks bottom limit"] = df2["close"] < df2["bottom limit"]

    # we get the indexes of the first valid (true) value on the "breaks limit"
    # column. If the index on "breaks top limit" is lowe than the index on
    # "breaks bottom limit" it means that it breaks the top limit before it breaks
    # the bottom one. In that case we label the day as bullish
    topBreakingIndexes = df2[["date", "breaks upper limit"]].replace(False, np.NaN).groupby("date").idxmax().replace(
        np.NaN, 999999999)
    bottomBreakingIndexes = df2[["date", "breaks bottom limit"]].replace(False, np.NaN).groupby(
        "date").idxmax().replace(np.NaN, 999999999)
    bullish = topBreakingIndexes.values.flatten() < bottomBreakingIndexes.values.flatten()

    dictMl = {'date': days.to_numpy().flatten().tolist(), "open": dOpen,
              "close": dClose, "min": dMin, "max": dMax,
              "bullish": bullish.astype(int)}
    dfMl = pd.DataFrame(dictMl).dropna()

    if return_full_dataFrame:
        return dfMl, dfCleaned
    else:
        return dfMl