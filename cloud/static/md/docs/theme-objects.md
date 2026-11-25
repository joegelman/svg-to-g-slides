# Theme objects and the theme builder

Applies to: SVG to Slides Chrome extension, version 1.3.0 and later.

Objects that come from the slide's layout or master are drawn on the slide but cannot be changed there. The Layers panel greys them and marks them **M**. A second click opens Slides' theme builder on the layout or master that holds the object.

## What a theme object is

A logo in the corner of every slide, a footer line, a background shape: these usually live on a layout or on the master, and Slides draws them on each slide that uses that layout. On the slide they look like any other object, but a click does not select them.

## How they are marked

In the [Layers panel](https://svgslid.es/docs/layers.md), theme objects are listed at the bottom, greyed, with an **M** badge. With Command held over the slide, a theme object gets a dashed amber outline in place of the blue one.

**To edit a theme object**

1. Click its row in the Layers panel. A message explains that the object belongs to the theme, and the row turns amber.
2. Click the row again within 5 seconds. Slides' theme builder opens on the layout or master that holds the object, with the object selected.
3. Make the change.
4. Press Option+Shift+M to go back to the slide.

A Command-click on a theme object on the slide follows the same two steps.

## The theme builder shortcut

Option+Shift+M opens the theme builder from any slide and returns from it. It is the same view that Slides opens from **View › Theme builder**.

> **Note:** A change made in the theme builder affects every slide that uses that layout or master.

## See also

- [The Layers panel](https://svgslid.es/docs/layers.md)
- [INFO: An object in Layers is greyed and marked M](https://svgslid.es/docs/kb/object-greyed-with-m.md)
- [Keyboard shortcuts](https://svgslid.es/docs/keyboard-shortcuts.md#anytime)

Source: https://svgslid.es/docs/theme-objects (SVG to Slides Documentation, User's Guide). Last reviewed November 24, 2026.
