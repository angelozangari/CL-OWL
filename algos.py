import networkx as nx
import math
import matplotlib.pyplot as plt

def _compute_colors_for_iteration(G: nx.Graph, table, iteration):
    """Helper function to compute colors for a specific iteration."""
    # Get WL values for specified iteration
    final_vals = [table[v]["vals"][iteration] for v in G.nodes()]

    # Normalize values to [0, 1] range
    min_val = min(final_vals)
    max_val = max(final_vals)
    val_range = max_val - min_val if max_val > min_val else 1

    # Create color mapping for each node
    colors = {}
    for node in G.nodes():
        node_val = table[node]["vals"][iteration]
        normalized = (node_val - min_val) / val_range  # 0 to 1

        # Map to color spectrum: red to cyan (half the color spectrum)
        hue = normalized * 180  # 0 to 180 degrees

        # Convert HSV to RGB (simplified)
        if hue <= 60:
            # Red to Yellow
            r, g, b = 255, int(hue * 255 / 60), 0
        elif hue <= 120:
            # Yellow to Green
            r, g, b = int((120 - hue) * 255 / 60), 255, 0
        else:
            # Green to Cyan
            r, g, b = 0, 255, int((hue - 120) * 255 / 60)

        colors[node] = (r/255, g/255, b/255)  # Matplotlib expects 0-1 range

    return colors

def wl(G: nx.Graph):
    """1D-WL algorithm implementation that stores colors in table."""
    num_iters = 0
    nodes = list(G.nodes())
    table = {v: {"vals": [1], "msgs": [], "colors": []} for v in nodes}  # table of messages of hashset and init 1 to all nodes vals

    # Compute initial colors for iteration 0
    initial_colors = _compute_colors_for_iteration(G, table, 0)
    for v in nodes:
        table[v]["colors"].append(initial_colors[v])

    while True:
        for v in nodes:
            neighbors = sorted(table[n]["vals"][-1] for n in G.neighbors(v))
            table[v]["msgs"].append((table[v]["vals"][-1], tuple(neighbors)))

        # compute vals (canonical relabel)
        uniq = sorted(set(table[v]["msgs"][-1] for v in nodes))
        id_map = {m: i for i, m in enumerate(uniq)}

        for v in G.nodes():
            table[v]["vals"].append(id_map[table[v]["msgs"][-1]])

        num_iters += 1

        # Compute colors for this iteration
        iter_colors = _compute_colors_for_iteration(G, table, num_iters)
        for v in nodes:
            table[v]["colors"].append(iter_colors[v])

        # stop condition
        if [table[v]["vals"][-1] for v in nodes] == [table[v]["vals"][-2] for v in nodes]:
            return num_iters, table

def plot(G: nx.Graph, iters: int, table, save_path: str = None):
    """Plot WL evolution across iterations."""
    cols = min(4, iters)
    rows = math.ceil(iters / cols)

    # Dynamic figure size based on number of subplots and graph size
    num_nodes = len(G.nodes())
    base_size = max(3, min(6, num_nodes * 0.3))  # Scale with graph size
    fig_width = cols * base_size
    fig_height = rows * base_size

    fig, axes = plt.subplots(rows, cols, figsize=(fig_width, fig_height))

    # Handle single subplot case
    if rows == 1 and cols == 1:
        axes = [axes]
    else:
        axes = axes.ravel()  # flatten axes if 2d

    # pos = nx.circular_layout(G)
    pos = nx.spring_layout(G, seed=0)
    # pos = nx.planar_layout(G)

    for i in range(iters):
        labels = {v: table[v]["vals"][i] for v in G.nodes()}

        # Get colors for this iteration from stored table
        node_colors = [table[node]["colors"][i] for node in G.nodes()]

        nx.draw(G, pos, labels=labels, with_labels=True, ax=axes[i],
                node_size=max(300, 2000//num_nodes), font_size=max(8, 16//max(1, num_nodes//5)),
                node_color=node_colors, font_weight='bold')
        axes[i].set_title(f"iter {i}")

    # Hide unused subplots
    for i in range(iters, len(axes)):
        axes[i].set_visible(False)

    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        plt.close()
    else:
        plt.show()


def rgb_to_color_name(rgb: list) -> str:
    """Convert RGB values to distinct color names for WL half-spectrum (Red→Cyan)."""
    r, g, b = rgb

    # Our WL algorithm should only generate colors in Red→Yellow→Green→Cyan range
    if b > 50 and r < 200 and g < 200:  # Blue-dominant (should not happen)
        raise ValueError(f"Unexpected color outside WL spectrum: RGB({r},{g},{b})")

    # Distinct single-word color names for Red→Cyan spectrum
    if r > 240 and g < 50 and b < 50:           # Pure red
        return "red"
    elif r > 200 and g < 120 and b < 50:       # Red-ish
        return "crimson"
    elif r > 200 and g > 100 and b < 50:       # Orange
        return "orange"
    elif r > 200 and g > 180 and b < 50:       # Yellow-ish orange
        return "amber"
    elif r > 200 and g > 200 and b < 50:       # Yellow
        return "yellow"
    elif r > 100 and g > 200 and b < 50:       # Green-ish yellow
        return "lime"
    elif r < 100 and g > 200 and b < 50:       # Green
        return "green"
    elif r < 50 and g > 200 and b > 100:       # Blue-green
        return "teal"
    elif r < 50 and g > 200 and b > 200:       # Cyan
        return "cyan"
    else:
        # Fallback for gradients
        if r > g:
            return "orange"
        else:
            return "lime"
