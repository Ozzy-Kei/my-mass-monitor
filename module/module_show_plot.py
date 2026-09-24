import matplotlib.pyplot as plt

def show_plot(data):
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(data["day"], data["weight"], marker="o", color="cornflowerblue")
    ax.set_xlabel("Date")
    ax.set_ylabel("Weight [kg]")
    ax.set_title(f"weight transition")
    ax.grid(True)
    plt.xticks(rotation=45)
    fig.tight_layout()
    return fig