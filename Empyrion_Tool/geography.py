from flask import Flask, send_file
import numpy as np
import matplotlib.pyplot as plt
import random

def generate_hex_grid(rows, cols):
    """Generate a hexagonal grid with random elevations."""
    hexes = {}
    for r in range(rows):
        for c in range(cols):
            x = c * 1.5  # Adjust spacing to form hex grid
            y = r * np.sqrt(3) + (c % 2) * (np.sqrt(3) / 2)  # Offset every other column
            elevation = random.randint(1, 100)  # Random elevation
            hexes[(r, c)] = {'x': x, 'y': y, 'elevation': elevation, 'river': False}
    return hexes

def find_lowest_neighbor(hexes, pos, rows, cols):
    """Find the lowest neighboring hex."""
    r, c = pos
    neighbors = [
        (r-1, c), (r+1, c), (r, c-1), (r, c+1),
        (r-1, c-1), (r+1, c+1) if c % 2 == 0 else (r-1, c+1), (r+1, c-1)
    ]
    neighbors = [(nr, nc) for nr, nc in neighbors if (nr, nc) in hexes]
    if not neighbors:
        return None
    return min(neighbors, key=lambda n: hexes[n]['elevation'])

def generate_rivers(hexes, rows, cols, num_rivers=5):
    """Simulate river generation from high points."""
    sorted_hexes = sorted(hexes.keys(), key=lambda k: -hexes[k]['elevation'])
    sources = sorted_hexes[:num_rivers]
    
    for source in sources:
        pos = source
        while pos:
            hexes[pos]['river'] = True
            next_pos = find_lowest_neighbor(hexes, pos, rows, cols)
            if next_pos and hexes[next_pos]['elevation'] < hexes[pos]['elevation']:
                pos = next_pos
            else:
                break

def plot_rivers(hexes, filename="river_map.png"):
    """Plot the hex grid and rivers and save to a file."""
    fig, ax = plt.subplots(figsize=(10, 10))
    for (r, c), data in hexes.items():
        color = 'blue' if data['river'] else 'lightgray'
        ax.scatter(data['x'], data['y'], color=color, s=50)
    ax.set_aspect('equal')
    plt.savefig(filename)
    plt.close()

app = Flask(__name__)

@app.route('/generate')
def generate_image():
    total_rows, total_cols = 10, 10
    hex_grid = generate_hex_grid(total_rows, total_cols)
    generate_rivers(hex_grid, total_rows, total_cols)
    plot_rivers(hex_grid)
    return send_file("river_map.png", mimetype='image/png')

if __name__ == '__main__':
    app.run(debug=True)
