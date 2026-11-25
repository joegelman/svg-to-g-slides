# Web Uploader

Applies to: SVG to Slides Web Uploader.

The Web Uploader converts SVG files on a web page, with nothing to install. Upload one file or a batch and get a Google Drive link to a file with one slide per SVG, every path a native shape.

**To convert SVG files online**

1. Open [svgslid.es/convert](https://svgslid.es/convert).
2. Drop your .svg files on the upload area, or click it to browse. Each file becomes one slide.
3. Optional: type a Google account address. The file is then shared straight to that account.
4. Click **Convert**. A link to the file in Google Drive appears.

![The Web Uploader page with a dashed upload area reading Drop SVG files here or click to browse, an optional Google account field and a Convert button](https://svgslid.es/static/docs/img/web-uploader.jpg)
Figure 1. The Web Uploader.

## Keeping the file

Links stay active for 7 days. After that the file is deleted.

**To keep a converted file**

1. Open the link.
2. In Google Drive, choose **File › Make a copy**.

The copy belongs to your account and does not expire.

## How it differs from the extension

|  | Web Uploader | Chrome extension |
|---|---|---|
| Where the result goes | A new file, one slide per SVG | The slide you have open |
| Gradients | Kept as gradients | Kept as gradients since version 1.4.0. First colour only before that |
| SVG text | Outlined into shapes. Not editable as text. | Not converted |
| Line icons that set the stroke on the whole SVG | Converted. Strokes become filled outline shapes. | Not converted |
| Where conversion runs | On the svgslid.es server | In your browser |
| Batch size | A batch | Up to 25 files per drop |

Clip paths, masks, patterns, filters and transparency do not come through on either. See [SVG feature support](https://svgslid.es/docs/svg-compatibility.md).

## What happens to your files

Uploaded SVG files are held only while the request runs and are deleted when it finishes. The converted file is stored in Google Drive for 7 days and shared by link. See [Permissions and data](https://svgslid.es/docs/permissions-privacy.md#web-uploader).

## See also

- [Workspace Add-on](https://svgslid.es/docs/add-on.md)
- [SVG feature support](https://svgslid.es/docs/svg-compatibility.md)
- [Permissions and data](https://svgslid.es/docs/permissions-privacy.md)
- [PRB: A Web Uploader link stops working after 7 days](https://svgslid.es/docs/kb/web-uploader-link-expired.md)
- [Guide: SVG to Google Slides converter](https://svgslid.es/guides/svg-to-google-slides-converter)

Source: https://svgslid.es/docs/web-uploader (SVG to Slides Documentation, Web Uploader and Add-on). Last reviewed November 24, 2026.
