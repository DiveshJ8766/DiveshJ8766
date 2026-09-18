# assets/

`portrait.txt` — the character grid the ASCII panel renders. Generated from
the GitHub avatar (subject mask from the cool-blue backdrop, local-contrast
tone mapping, then quantised to the density ramp). `make_ascii_svg.py` reads
it directly, so no image libraries are needed at render time.

To regenerate from a higher-resolution photo instead:

    pip install -r scripts/requirements-portrait.txt
    python scripts/prep_photo.py my-photo.jpg     # writes assets/portrait.png
    rm assets/portrait.txt                        # portrait.png then wins
    cd scripts && python make_ascii_svg.py

Delete both and the script falls back to a DJ monogram placeholder.
