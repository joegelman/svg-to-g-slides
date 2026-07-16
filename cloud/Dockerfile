FROM python:3.12-slim

WORKDIR /app

# Inkscape for stroke-to-path preprocessing
RUN apt-get update && apt-get install -y --no-install-recommends inkscape \
    && rm -rf /var/lib/apt/lists/*

# Install deps first (layer cache)
COPY cloud/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy converter core + cloud service files
COPY svg_to_slides.py    ./svg_to_slides.py
COPY cloud/main.py       ./main.py
COPY cloud/drive.py      ./drive.py
COPY cloud/slides_clip.py ./slides_clip.py
COPY cloud/static/       ./static/

ENV PORT=8080
EXPOSE 8080

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
