# Command reference

Applies to: SVG to Slides Chrome extension, version 1.3.0.

Availability: Version 1.3.0 is not in the Chrome Web Store yet. The store installs version 1.2.0. See [what each version has](https://svgslid.es/docs/release-notes.md#matrix).

Every command the toolbar and the command palette offer, by group, with what each one needs selected.

## Tools and panels

| Command | What it does | Needs selected | Shortcut (Mac) |
|---|---|---|---|
| Show or hide the toolbar | Opens or closes the toolbar. | Nothing | Option+\ |
| Command palette | Lists every command with its shortcut. | Nothing | Command+\ |
| Show or hide Layers | Opens or closes the Layers panel. | Nothing | Option+1 |
| Pen | Draws new shapes, or opens the editor on the selection with the pen active. | Nothing | Option+Shift+P |
| Theme builder, and back | Opens Slides' theme builder on the slide's layout, or returns to the slide. | Nothing | Option+Shift+M |
| Edit Shape | Opens the point editor on the selection. Double-click a shape, then click Edit Shape. | A shape |  |
| Select inside a group | Command-click selects the innermost object under the pointer. Shift+Command-click adds. | Nothing |  |
| Undo one of the extension's changes | Undoes a multi-step change in one press. | Right after the change | Command+Z |
| Redo it | Redoes it in one press. Command+Y does the same. | Right after an undo | Shift+Command+Z |

## Align and distribute

| Command | What it does | Needs selected | Shortcut (Mac) |
|---|---|---|---|
| Align left | Aligns left edges. One object: to the slide's left edge. | One object or more | Option+A |
| Align centres horizontally | Aligns centres on a vertical line. One object: centres it on the page. | One object or more | Option+H |
| Align right | Aligns right edges. One object: to the slide's right edge. | One object or more | Option+D |
| Align top | Aligns top edges. One object: to the slide's top edge. | One object or more | Option+W |
| Align middles vertically | Aligns middles on a horizontal line. One object: centres it on the page. | One object or more | Option+V |
| Align bottom | Aligns bottom edges. One object: to the slide's bottom edge. | One object or more | Option+S |
| Distribute horizontal spacing | Evens out the horizontal gaps. | Three objects or more | Option+Shift+H |
| Distribute vertical spacing | Evens out the vertical gaps. | Three objects or more | Option+Shift+V |

## Combine

| Command | What it does | Needs selected | Shortcut (Mac) |
|---|---|---|---|
| Union | One shape covering everything the selected shapes cover. | Two shapes or more | Option+Shift+U |
| Subtract | The bottom shape with the shapes above it cut out. | Two shapes or more | Option+Shift+S |
| Intersect | Only the area where the shapes overlap. | Two shapes or more | Option+Shift+I |
| Exclude | Everything except the area where the shapes overlap. | Two shapes or more | Option+Shift+E |

## Group and mask

| Command | What it does | Needs selected | Shortcut (Mac) |
|---|---|---|---|
| Group | Groups the selection. | Two objects or more | Command+Option+G |
| Ungroup | Ungroups the selected group. | A group | Shift+Command+Option+G |
| Mask image with shape | The shape on top cuts out the picture under it. | One image and one shape or group | Option+Shift+K |

## Outline

| Command | What it does | Needs selected | Shortcut (Mac) |
|---|---|---|---|
| Outline stroke | Turns a stroke into a filled shape. | A shape or line with a stroke | Option+Command+O |
| Outline text | Turns text into shapes. | An object with text | Option+Command+T |
| Restore outlined text | Puts outlined text back as live text. | Text outlined on this computer | Option+Command+T |

## Fill and stroke

| Command | What it does | Needs selected | Shortcut (Mac) |
|---|---|---|---|
| Fill colour | Opens Slides' fill colour menu. | A shape | Option+Shift+F |
| Stroke colour | Opens Slides' border colour menu. | A shape or line | Option+Shift+L |
| Stroke on / off | Removes the stroke or puts it back. | A shape or line | Option+Shift+/ |
| Thinner stroke | Steps the stroke weight down. | A shape or line | Option+Shift+[ |
| Thicker stroke | Steps the stroke weight up. | A shape or line | Option+Shift+] |
| Centre stroke | Puts the stroke back on the outline. | A closed shape with a stroke |  |
| Inside stroke | Moves the stroke inside the outline. | A closed shape with a stroke |  |
| Outside stroke | Moves the stroke outside the outline. | A closed shape with a stroke |  |

## Arrange, rotate and resize

| Command | What it does | Needs selected | Shortcut (Mac) |
|---|---|---|---|
| Bring to front | Moves the selection to the top of the stack. | An object | Shift+Command+Up Arrow |
| Bring forward | Moves the selection up one place. | An object | Command+Up Arrow |
| Send backward | Moves the selection down one place. | An object | Command+Down Arrow |
| Send to back | Moves the selection to the bottom of the stack. | An object | Shift+Command+Down Arrow |
| Rotate 15° left or right | Rotates the selection. Option+Right Arrow rotates the other way. | An object | Option+Left Arrow |
| Rotate 1° left or right | Rotates in fine steps. Option+Shift+Right Arrow rotates the other way. | An object | Option+Shift+Left Arrow |
| Make larger | Resizes the selection up. | An object | Command+Control+K |
| Make smaller | Resizes the selection down. | An object | Command+Control+J |


## Messages

When a command cannot run, the extension shows a short message under the toolbar that says what to select. Examples: "Select two or more objects to group", "Select three or more objects to distribute", "Nothing selected has text".

## See also

- [Keyboard shortcuts](https://svgslid.es/docs/keyboard-shortcuts.md)
- [The command palette](https://svgslid.es/docs/command-palette.md)
- [The toolbar](https://svgslid.es/docs/toolbar.md)
- [Limits and known issues](https://svgslid.es/docs/limits.md)

Source: https://svgslid.es/docs/commands (SVG to Slides Documentation, Reference). Last reviewed November 20, 2026.
