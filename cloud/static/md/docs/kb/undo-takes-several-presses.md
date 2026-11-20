# PRB: COMMAND+Z undoes only part of a combine or outline

Article ID: Q100109. Last reviewed: November 20, 2026.

Applies to: SVG to Slides Chrome extension, version 1.3.0.

Availability: Version 1.3.0 is not in the Chrome Web Store yet. The store installs version 1.2.0. See [what each version has](https://svgslid.es/docs/release-notes.md#matrix).

A combine, outline or mask is several steps inside Slides. The extension undoes them in one press only while the slide is as it left it. If you changed the slide afterwards, Slides' own undo takes over and goes one step per press. Keep pressing COMMAND+Z until the original returns.

## Symptoms

You press Command+Z after a Union, an Outline or a Mask. Shapes disappear or reappear one at a time and the slide passes through states you did not make.

## Cause

The change reached Slides as several steps: remove the originals, insert the result, restore its place in the stack. The extension undoes all of them in one press, but only right after the change. Once you change the slide yourself, the extension stops, because pressing undo for you could remove your own work.

## Resolution

Keep pressing Command+Z until the slide is back to where you want it. Nothing is lost. The steps are in Slides' own history.

## Status

This behaviour is by design.

## More information

In version 1.2.0, which had no one-press undo, undoing an Edit Shape session always took several presses.

## See also

- [Undo and redo](https://svgslid.es/docs/undo-redo.md)
- [Multi-step changes and undo](https://svgslid.es/docs/undo-and-still-copy.md#undo)

Source: https://svgslid.es/docs/kb/undo-takes-several-presses (SVG to Slides Documentation, Knowledge Base). Last reviewed November 20, 2026.
