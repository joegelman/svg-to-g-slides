#!/bin/bash
# Double-click this file in Finder to install svg-to-slides.
# Can also be run from Terminal: bash Install.command

set -e
REPO_DIR="$(cd "$(dirname "$0")" && pwd)"

BIN_DIR="$HOME/.local/bin"
LIB_DIR="$HOME/.local/share/svg-to-slides/lib"
SCRIPTS_DIR="$HOME/Library/Scripts"
AGENTS_DIR="$HOME/Library/LaunchAgents"
CONF_FILE="$HOME/.config/svg-to-slides.conf"
DROP_DIR="$HOME/Library/Application Support/svg-to-slides-drop"
LABEL="com.${USER}.svg-to-slides"
PLIST="$AGENTS_DIR/$LABEL.plist"

# Keep Terminal window open so the user can read the output
trap 'echo ""; read -rp "Press Return to close this window. " _' EXIT

# Apply custom icon to this file (persists in Finder; git won't track it)
_icon="$REPO_DIR/assets/icon.png"
if [[ -f "$_icon" ]] && command -v fileicon >/dev/null 2>&1; then
  fileicon set "$REPO_DIR/Install.command" "$_icon" 2>/dev/null || true
fi

echo "=== svg-to-slides installer ==="
echo ""

# ── Dependencies ──────────────────────────────────────────────────────────────

if ! command -v python3 >/dev/null 2>&1; then
  echo "ERROR: python3 not found."
  echo "Install Xcode Command Line Tools first:"
  echo "  xcode-select --install"
  exit 1
fi

if ! command -v pip3 >/dev/null 2>&1; then
  echo "ERROR: pip3 not found."
  echo "Install Xcode Command Line Tools first:"
  echo "  xcode-select --install"
  exit 1
fi

# ── Inkscape (for text outlining and stroke-to-path) ──────────────────────────

if command -v inkscape >/dev/null 2>&1; then
  echo "✓ Inkscape already installed"
elif command -v brew >/dev/null 2>&1; then
  echo "Installing Inkscape via Homebrew (this may take a few minutes)..."
  brew install --cask inkscape
  echo "✓ Inkscape installed"
else
  echo "⚠ Inkscape not found and Homebrew is not installed."
  echo "  Text in SVGs will be skipped during conversion."
  echo "  To add text support, install Homebrew then run:"
  echo "    brew install --cask inkscape"
fi

# ── Python deps (local install — no sudo, no --break-system-packages) ─────────

echo "Installing Python dependencies..."
mkdir -p "$LIB_DIR"
pip3 install --quiet --target "$LIB_DIR" python-pptx lxml
echo "✓ python-pptx + lxml → $LIB_DIR"

# ── Scripts ───────────────────────────────────────────────────────────────────

mkdir -p "$BIN_DIR"
cp "$REPO_DIR/svg_to_slides.py" "$BIN_DIR/svg_to_slides.py"
chmod +x "$BIN_DIR/svg_to_slides.py"
cp "$REPO_DIR/png_to_svg.sh" "$BIN_DIR/png_to_svg.sh"
chmod +x "$BIN_DIR/png_to_svg.sh"
echo "✓ Scripts → $BIN_DIR/"

# ── Drop folder ───────────────────────────────────────────────────────────────

mkdir -p "$DROP_DIR"
echo "✓ Drop folder ready"

# ── Configuration (auto-detect Google Drive) ──────────────────────────────────

if [[ ! -f "$CONF_FILE" ]]; then
  mkdir -p "$(dirname "$CONF_FILE")"

  drive_base=""
  for d in "$HOME/Library/CloudStorage/GoogleDrive-"*/My\ Drive; do
    [[ -d "$d" ]] && { drive_base="$d"; break; }
  done

  echo "DROP_DIR=\"$DROP_DIR\"" > "$CONF_FILE"
  if [[ -n "$drive_base" ]]; then
    drive_dir="$drive_base/SVG to Slides"
    echo "DRIVE_DIR=\"$drive_dir\"" >> "$CONF_FILE"
    mkdir -p "$drive_dir"
    echo "✓ Google Drive detected → $drive_dir"
  else
    echo "  Google Drive not detected — PPTX files will stay in the drop folder."
    echo "  Once Drive is installed, add this line to ~/.config/svg-to-slides.conf:"
    echo "    DRIVE_DIR=\"\$HOME/Library/CloudStorage/GoogleDrive-you@gmail.com/My Drive/SVG to Slides\""
  fi
else
  echo "✓ Config already exists (skipped)"
fi

# ── Watcher script ────────────────────────────────────────────────────────────

mkdir -p "$SCRIPTS_DIR"
cp "$REPO_DIR/watch/watcher.sh" "$SCRIPTS_DIR/svg_to_slides_watch.sh"
chmod +x "$SCRIPTS_DIR/svg_to_slides_watch.sh"
echo "✓ Watcher → $SCRIPTS_DIR/"

# ── launchd agent ─────────────────────────────────────────────────────────────

mkdir -p "$AGENTS_DIR"
sed "s/__USER__/$USER/g" "$REPO_DIR/watch/com.user.svg-to-slides.plist" > "$PLIST"
launchctl unload "$PLIST" 2>/dev/null || true
launchctl load "$PLIST"
echo "✓ Background agent loaded (polls every 5 s)"

# ── Desktop shortcut (symlink — Finder aliases misresolve on some systems) ────

ALIAS="$HOME/Desktop/SVG to Slides Drop"
if [[ ! -e "$ALIAS" ]]; then
  ln -s "$DROP_DIR" "$ALIAS"
  echo "✓ Desktop shortcut created"
else
  echo "✓ Desktop shortcut already exists (skipped)"
fi

echo ""
echo "All done. Drag .svg files onto 'SVG to Slides Drop' on your Desktop."
echo "Watch the log:  tail -f /tmp/svg-to-slides.log"
