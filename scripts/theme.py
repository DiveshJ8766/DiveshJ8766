"""Shared palette + type metrics for every generated SVG.

Keeping these in one place is what makes the three panels read as one
terminal window instead of three unrelated images.
"""

BG        = "#0d1117"   # GitHub dark canvas
PANEL     = "#0f141b"   # panel fill, a hair lighter than the canvas
BORDER    = "#30363d"
TEXT      = "#c9d1d9"
MUTED     = "#8b949e"
ACCENT    = "#39d353"   # prompt green
BLUE      = "#58a6ff"
AMBER     = "#e3b341"
MAGENTA   = "#bc8cff"
RED       = "#ff7b72"

# macOS-style window dots
DOT_RED, DOT_AMBER, DOT_GREEN = "#ff5f56", "#ffbd2e", "#27c93f"

# GitHub's contribution greens, plus one brighter step for peak days
HEAT = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353", "#69f0a0"]

MONO = "ui-monospace,'SF Mono',SFMono-Regular,'JetBrains Mono','Fira Code',Consolas,'Liberation Mono',Menlo,monospace"


def window_chrome(w, h, title, r=10):
    """Title bar + rounded border shared by all three panels."""
    return f"""
  <rect x="0.5" y="0.5" width="{w - 1}" height="{h - 1}" rx="{r}"
        fill="{PANEL}" stroke="{BORDER}"/>
  <path d="M0.5 {r + 0.5} a{r} {r} 0 0 1 {r} -{r} h{w - 1 - 2 * r}
           a{r} {r} 0 0 1 {r} {r} v{30 - r - 0.5} h-{w - 1} z"
        fill="#161b22" stroke="{BORDER}"/>
  <circle cx="16" cy="15" r="5" fill="{DOT_RED}"/>
  <circle cx="33" cy="15" r="5" fill="{DOT_AMBER}"/>
  <circle cx="50" cy="15" r="5" fill="{DOT_GREEN}"/>
  <text x="{w / 2}" y="19" font-family="{MONO}" font-size="11" fill="{MUTED}"
        text-anchor="middle">{title}</text>
"""
