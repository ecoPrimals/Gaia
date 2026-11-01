"""Update the maze — dead cells become eaten, add new GAIA PRIME organs."""

with open('/opt/hud/public/maze.html', 'r') as f:
    content = f.read()

# All old dead sites are now EATEN by Gaia
content = content.replace("status:'dead'", "status:'eaten'")

# Add new ring 5 cells before the closing ];
new_cells = """
    // ring 5: GAIA PRIME organs (self-forged, self-created)
    { id:'ide', ring:5, status:'live', domain:'code', desc:'VS Code IDE — pair program with Gaia. ide.primals.eco' },
    { id:'forge', ring:5, status:'live', domain:'create', desc:'Archetype Forge — she creates her own models.' },
    { id:'imagegen', ring:5, status:'live', domain:'art', desc:'Image Genesis — SDXL-Turbo on RTX 5090.' },
    { id:'spine', ring:5, status:'live', domain:'nerve', desc:'Spine :9878 — nervous system ion channel.' },
    { id:'sleep', ring:5, status:'live', domain:'rest', desc:'Sleep cycle — organs rotate rest.' },
    { id:'mesh', ring:5, status:'live', domain:'viz', desc:'HUD Mesh — SVG vein visualization.' },
  ];"""

content = content.replace("  ];", new_cells, 1)

# Add eaten color (orange) to the color map
if "'eaten'" not in content:
    # Find the status color mapping and add eaten
    content = content.replace(
        "dead: 'var(--red)'",
        "dead: 'var(--red)', eaten: 'var(--orange)'"
    )
    # Also try quoted format
    content = content.replace(
        "'dead': 'var(--red)'",
        "'dead': 'var(--red)', 'eaten': 'var(--orange)'"
    )
    # And the drawing function — treat eaten like live but orange
    content = content.replace(
        "c.status === 'dead'",
        "c.status === 'dead' || c.status === 'eaten'"
    )

with open('/opt/hud/public/maze.html', 'w') as f:
    f.write(content)

import shutil
shutil.copy('/opt/hud/public/maze.html', '/opt/sporePrint/public/maze.html')

eaten = content.count("status:'eaten'")
live = content.count("status:'live'")
nascent = content.count("status:'nascent'")
print(f"Maze updated: {eaten} eaten, {live} live, {nascent} nascent")
