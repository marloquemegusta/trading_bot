def LimitBreakings(limits, df):
    import numpy as np
    df["upper limit"] = np.NaN
    df["bottom limit"] = np.NaN
    df["stretch"] = np.NaN

    # opening of the first period of the day and thus, opening of the day
    dOpen = df.groupby("date").first().open.values

    # dayIndex contains the index of the first period of each day in df
    dayIndex = df["date"].drop_duplicates().index

    # we place the stretch and limits (open of the day +- stretch) on the first
    # period of each day

    df.loc[dayIndex, "stretch"] = limits
    df.loc[dayIndex, "upper limit"] = (dOpen + limits)
    df.loc[dayIndex, "bottom limit"] = (dOpen - limits)

    # we place both limits at the openning of the day at minute N(500 in this case)
    N = 500
    df.loc[dayIndex + N, "upper limit"] = dOpen
    df.loc[dayIndex + N, "bottom limit"] = dOpen

    # finally, we perform a forward fill  by filling all NaN value with the last
    # valid value
    df = df.fillna(method='ffill')
    # for each period (minutes in this case) we define a flag to indicate wheter
    # it ends up above upper limit or bellow bottom limit
    df["breaks upper limit"] = df["close"] > df["upper limit"]
    df["breaks bottom limit"] = df["close"] < df["bottom limit"]

    # we get the indexes of the first valid (true) value on the "breaks limit"
    # column. If the index on "breaks top limit" is lowe than the index on
    # "breaks bottom limit" it means that it breaks the top limit before it breaks
    # the bottom one. In that case we label the day as bullish
    topBreakingIndexes = df[["date", "breaks upper limit"]].replace(False, np.NaN).groupby("date").idxmax().replace(
        np.NaN, 999999999)
    bottomBreakingIndexes = df[["date", "breaks bottom limit"]].replace(False, np.NaN).groupby(
        "date").idxmax().replace(np.NaN, 999999999)
    firstBreakingIndex=np.minimum(topBreakingIndexes,bottomBreakingIndexes).values.flatten()
    return firstBreakingIndex
