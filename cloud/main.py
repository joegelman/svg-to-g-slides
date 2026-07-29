"""svg-to-slides cloud service — FastAPI backend."""
import base64
import os
import secrets
import sys
import tempfile
from pathlib import Path

from fastapi import FastAPI, File, Form, Header, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

# Pull in svg_to_slides from the repo root (one level up)
sys.path.insert(0, str(Path(__file__).parent.parent))
from svg_to_slides import convert  # noqa: E402
from slides_clip import build_clip_bundle, build_clip_bundle_at  # noqa: E402

from drive import delete_old_files, upload_and_share  # noqa: E402

RETENTION_DAYS = int(os.environ.get("RETENTION_DAYS", "7"))
MAX_INSERT_FILES = 25  # grid layout is only reasonable up to this many at once; more should use the bulk uploader

app = FastAPI(title="svg-to-slides")

# Every endpoint here is already fully unauthenticated/public (no cookies or
# auth headers involved), so a wildcard origin costs nothing and lets the
# Chrome extension's popup (origin chrome-extension://<id>) call this API
# directly. (Extension contexts with matching host_permissions can usually
# bypass CORS on their own, but that's version-dependent Chrome behavior —
# this makes it work regardless.) Not combined with allow_credentials=True,
# which Starlette rejects alongside a wildcard origin anyway.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
def index():
    return FileResponse("static/index.html")


@app.get("/health")
def health():
    return {"ok": True}


@app.get("/privacy")
def privacy():
    return FileResponse("static/privacy.html")


@app.get("/terms")
def terms():
    return FileResponse("static/terms.html")


@app.get("/features")
def features():
    # Not linked from the homepage nav yet — reachable directly by URL only.
    return FileResponse("static/features.html")


@app.get("/guide")
def guide():
    return FileResponse("static/guide.html")


@app.get("/support")
def support():
    return FileResponse("static/support.html")


@app.get("/chrome")
def chrome_redirect():
    # authuser/hl query params stripped — those were session-specific to
    # whichever Google account/locale was active when the link was grabbed.
    return RedirectResponse("https://chromewebstore.google.com/detail/svg-to-slides/bdhhnakellmdnbgbdokiojipaebdeioi")


@app.post("/cleanup")
def cleanup(x_cleanup_token: str = Header(default="")):
    """Delete output files older than RETENTION_DAYS from the Drive output folder.

    Invoked on a schedule by Cloud Scheduler (see cloud/deploy.sh). Gated by a shared
    secret since the whole Cloud Run service runs with --allow-unauthenticated.
    """
    expected = os.environ.get("CLEANUP_TOKEN", "")
    if not expected or not secrets.compare_digest(x_cleanup_token, expected):
        raise HTTPException(status_code=403, detail="Forbidden")

    folder_id = os.environ.get("DRIVE_FOLDER_ID")
    if not folder_id:
        raise HTTPException(status_code=500, detail="DRIVE_FOLDER_ID not configured")

    deleted = delete_old_files(folder_id, max_age_days=RETENTION_DAYS)
    return JSONResponse({"deleted": len(deleted)})


@app.post("/convert")
async def convert_endpoint(
    files: list[UploadFile] = File(...),
    email: str = Form(""),
):
    svg_files = [f for f in files if f.filename.lower().endswith(".svg")]
    if not svg_files:
        raise HTTPException(status_code=400, detail="No .svg files provided.")

    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)

        # Write uploaded files to temp dir
        saved = []
        for uf in svg_files:
            dest = tmp_path / Path(uf.filename).name
            dest.write_bytes(await uf.read())
            saved.append(str(dest))

        # Convert
        out_pptx = convert(saved, out_dir=tmp)
        if out_pptx is None or not out_pptx.exists():
            raise HTTPException(status_code=500, detail="Conversion failed.")

        # Upload to Drive and share
        try:
            link = upload_and_share(out_pptx, email=email or None)
        except Exception as exc:
            raise HTTPException(status_code=502, detail=f"Drive upload failed: {exc}")

    return JSONResponse({"link": link, "retention_days": RETENTION_DAYS})


# ── Add-on insert endpoint ─────────────────────────────────────────────────────

class _SvgFile(BaseModel):
    name: str
    data: str  # base64-encoded SVG content

class _InsertRequest(BaseModel):
    files: list[_SvgFile]
    slide_width_pt:  float | None = None  # active presentation width in points
    slide_height_pt: float | None = None  # active presentation height in points

_PT_TO_EMU = 12700

@app.post("/insert-svg")
async def insert_svg_endpoint(req: _InsertRequest):
    """Accept SVG files (base64 JSON), return the resulting PPTX as base64.

    DEPRECATED: kept only as a fidelity-comparison reference for the new
    /insert-svg-clip endpoint (see cloud/slides_clip.py) during verification;
    the add-on no longer calls this. Remove once fidelity is confirmed.
    """
    svg_files = [f for f in req.files if f.name.lower().endswith(".svg")]
    if not svg_files:
        raise HTTPException(status_code=400, detail="No .svg files provided.")

    slide_w = int(req.slide_width_pt  * _PT_TO_EMU) if req.slide_width_pt  else None
    slide_h = int(req.slide_height_pt * _PT_TO_EMU) if req.slide_height_pt else None

    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        saved = []
        for f in svg_files:
            dest = tmp_path / Path(f.name).name
            dest.write_bytes(base64.b64decode(f.data))
            saved.append(str(dest))

        out_pptx = convert(saved, out_dir=tmp, slide_w=slide_w, slide_h=slide_h)
        if out_pptx is None or not out_pptx.exists():
            raise HTTPException(status_code=500, detail="Conversion failed.")

        pptx_b64 = base64.b64encode(out_pptx.read_bytes()).decode()

    return JSONResponse({"pptx": pptx_b64})


@app.post("/insert-svg-clip")
async def insert_svg_clip_endpoint(req: _InsertRequest):
    """Accept SVG files (base64 JSON) + the active presentation's size, return
    Google Slides' internal clipboard payload for the converted shapes.

    Called exclusively by the Google Slides add-on. No Drive/Slides API call
    happens anywhere in this path — the add-on writes the returned bundle to
    the OS clipboard client-side and the user pastes with Cmd/Ctrl+V. See
    cloud/slides_clip.py for how the payload is built and why this needs no
    OAuth scope at all.
    """
    svg_files = [f for f in req.files if f.name.lower().endswith(".svg")]
    if not svg_files:
        raise HTTPException(status_code=400, detail="No .svg files provided.")
    if not req.slide_width_pt or not req.slide_height_pt:
        raise HTTPException(status_code=400, detail="slide_width_pt and slide_height_pt are required.")

    sources = [(f.name, base64.b64decode(f.data)) for f in svg_files]
    bundle = build_clip_bundle(sources, req.slide_width_pt, req.slide_height_pt)

    return JSONResponse({"clip": bundle})


class _InsertAtRequest(BaseModel):
    files: list[_SvgFile]
    x_pt: float
    y_pt: float
    box_w_pt: float
    box_h_pt: float


@app.post("/insert-svg-clip-at")
async def insert_svg_clip_at_endpoint(req: _InsertAtRequest):
    """Same clipboard payload as /insert-svg-clip, but for the Chrome
    extension: aspect-fits each SVG into a box (box_w_pt, box_h_pt) centered
    at (x_pt, y_pt), rather than fitting to a given slide's real dimensions.
    No slide-dimension or DOM-derived parameter exists on this endpoint at
    all — the extension estimates the box/position itself from the browser
    window size and an assumed default slide size, so it needs zero Google
    OAuth scopes anywhere in this path.
    """
    svg_files = [f for f in req.files if f.name.lower().endswith(".svg")]
    if not svg_files:
        raise HTTPException(status_code=400, detail="No .svg files provided.")
    if len(svg_files) > MAX_INSERT_FILES:
        raise HTTPException(
            status_code=400,
            detail=f"Too many files for a single insert (max {MAX_INSERT_FILES}) — use the bulk uploader instead.",
        )

    sources = [(f.name, base64.b64decode(f.data)) for f in svg_files]
    bundle = build_clip_bundle_at(sources, req.x_pt, req.y_pt, req.box_w_pt, req.box_h_pt)

    return JSONResponse({"clip": bundle})
