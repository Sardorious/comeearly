from matplotlib.figure import Figure


def save_img(name: str) -> str:
    fig = Figure()
    ax = fig.subplots()
    ax.plot([1, 2, 3, 4])
    fig.savefig(f"{name}.jpg", format="jpg", bbox_inches="tight")
    return f"{name}.jpg"
