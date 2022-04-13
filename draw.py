import matplotlib
import matplotlib.pyplot as plt

matplotlib.use('Agg')


def save_img(name: str) -> str:
    fig, ax = plt.subplots()
    ax.plot([1, 2, 3, 4])
    plt.savefig(f"{name}.jpg", format="jpg", bbox_inches="tight")
    return f"{name}.jpg"
