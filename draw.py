import io

import matplotlib
import matplotlib.dates as mdates
from matplotlib.figure import Figure

matplotlib.use("agg")


def save_img(x, y, minT, maxT):
    x = mdates.datestr2num(x)
    y = mdates.datestr2num(y)
    mean_t = (minT + maxT) / 2
    interval_t = (minT - maxT) / 2

    fig = Figure()
    ax = fig.subplots()
    ax2 = ax.twinx()

    ax.scatter(x, y)
    ax.grid(True, axis="y")
    ax.xaxis_date()
    ax.yaxis_date()
    ax.set_xticks(x)
    ax.set_ylabel("Interval with 09:00")  # y label

    ax2.errorbar(
        x,
        mean_t,
        yerr=interval_t,
        fmt=".",
        capsize=5,
        color="k",
    )
    ax2.set_ylabel("\U00002103")  # y label

    fig.autofmt_xdate()

    buf = io.BytesIO()
    fig.savefig(buf, format="jpg", bbox_inches="tight")
    buf.seek(0)
    return buf
