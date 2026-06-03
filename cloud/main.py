"""svg-to-slides cloud service — FastAPI backend."""
import sys
import tempfile
from pathlib import Path

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

# Pull in svg_to_slides from the repo root (one level up)
sys.path.insert(0, str(Path(__file__).parent.parent))
from svg_to_slides import convert  # noqa: E402

from drive import upload_and_share  # noqa: E402

app = FastAPI(title="svg-to-slides")
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
def index():
    return FileResponse("static/index.html")


@app.get("/health")
def health():
    return {"ok": True}


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

    return JSONResponse({"link": link})
