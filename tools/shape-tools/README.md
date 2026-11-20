# Shape tools build (extension 1.3)

Builds the two bundled libraries the Shape tools rail uses:

- `extension/geo-ops.js`: Paper.js + paperjs-offset + `src/geo.js` (booleans, stroke outlines, glyph paths)
- `extension/fontkit.js`: fontkit, for reading glyph outlines from TTF/OTF/WOFF/WOFF2 bytes

```
cd tools/shape-tools
npm install
npm test        # builds into ../../extension and runs the geometry tests
```

`extension/shape-tools.js` is plain source and needs no build. Commit the generated files with the change that needs them.
