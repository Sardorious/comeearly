import io

import matplotlib
import pandas as pd
import seaborn as sns
import scipy as sp
from matplotlib.dates import DateFormatter, MinuteLocator, datestr2num
from matplotlib.figure import Figure

matplotlib.use("agg")


def export_plt(fig, is_buf=True):
    if is_buf:
        buffer = io.BytesIO()
        fig.savefig(buffer, format="jpg", bbox_inches="tight")
        buffer.seek(0)
        return buffer
    else:
        fig.savefig("tempfile.jpg", format="jpg", bbox_inches="tight")
        return None


def plot_timeseries(df: pd.DataFrame, title: str, is_buf=True):
    x = datestr2num(df["date"])
    y = datestr2num(df["check_time"])
    mean_t = (df["minT"] + df["maxT"]) / 2
    interval_t = (df["minT"] - df["maxT"]) / 2

    fig = Figure()
    ax = fig.subplots()
    ax2 = ax.twinx()
    ax.set_zorder(1)
    ax.patch.set_visible(False)

    ax.scatter(x, y, c="royalblue")

    ax.grid(True, axis="y")
    ax.set_axisbelow(True)

    ax.set_title(f"{title} check time & temperature plot")

    ax.xaxis.set_ticks(x)
    ax.xaxis.set_major_formatter(DateFormatter("%Y-%m-%d"))

    ax.yaxis.set_major_locator(MinuteLocator(byminute=range(0, 60, 2)))
    ax.yaxis.set_major_formatter(DateFormatter("%H:%M:%S"))
    ax.yaxis.set_label_text("Check in time")

    ax2.errorbar(
        x,
        mean_t,
        yerr=interval_t,
        fmt=".",
        capsize=5,
        color="darkorange",
    )
    ax2.yaxis.set_label_text("\U00002103")  # y label

    fig.autofmt_xdate()

    return export_plt(fig, is_buf)


def plot_reg(df: pd.DataFrame, title: str, is_buf=True):
    x = datestr2num(df["check_time"])
    y = (df["minT"] + df["maxT"]) / 2
    slope, intercept, r_value, p_value, std_err = sp.stats.linregress(x, y)

    fig = Figure()
    ax = fig.subplots()

    sns.regplot(x=x, y=y, truncate=False, ax=ax)

    ax.grid(True, axis="y")
    ax.set_axisbelow(True)

    ax.set_title(f"{title} check time / temperature regression plot")
    ax.text(
        0.85,
        0.05,
        f"R={r_value:.3f}",
        transform=ax.transAxes,
        bbox=dict(facecolor='none', edgecolor='k', boxstyle='round')
    )

    ax.xaxis.set_major_locator(MinuteLocator(byminute=range(0, 60, 2)))
    ax.xaxis.set_major_formatter(DateFormatter("%H:%M:%S"))
    ax.xaxis.set_label_text("Check-in time")  # y label

    ax.yaxis.set_label_text("\U00002103")  # y label

    fig.autofmt_xdate()

    return export_plt(fig, is_buf)
