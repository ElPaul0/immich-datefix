# immich-datefix

Companion tool for [Immich](https://immich.app): fix capture dates when the **filename** contains the real date (WhatsApp, screenshots, Unix timestamps, .NET ticks…) but Immich / EXIF is wrong or missing.

Not an Immich plugin — a small container in the same Docker stack, talking to the Immich API.

**Image:** [`ghcr.io/elpaul0/immich-datefix`](https://github.com/ElPaul0/immich-datefix/pkgs/container/immich-datefix)

## Features

- Local users with a **PIN** — each account stores its Immich API key
- Login / logout via cookie session (no need to re-paste the key)
- **Dark / light** UI (matte greys) and **EN / FR** language toggle
- Scan the whole library via Immich API (results are **not** kept across refresh; re-scan after apply to verify)
- Detect known filename patterns
- Checkbox UI: choose which pattern families to fix
- Dry-run then apply (`dateTimeOriginal` bulk update)
- Only proposes changes when the delta exceeds 12 hours (configurable)

## Patterns

| Id | Example |
|----|---------|
| whatsapp | `IMG-20261002-WA0001.jpg` |
| screenshot | `Screenshot_20261002-143015.png` |
| pixel | `PXL_20261002_143015123.jpg` |
| img_underscore | `IMG_20261002_143015.jpg` |
| yyyymmdd_hhmmss | `20261002_143015.jpg` |
| iso_filename | `2026-10-02_14-30-15.jpg` |
| unix_ms / unix_s | epoch in filename |
| dotnet_ticks | Facebook-like 18-digit ticks |

## Quick start (same stack as Immich)

```yaml
  immich-datefix:
    container_name: immich_datefix
    image: ghcr.io/elpaul0/immich-datefix:latest
    restart: always
    ports:
      - "2284:8080"
    environment:
      IMMICH_URL: http://immich-server:2283
      TZ: Europe/Paris
    volumes:
      - /mnt/data/immich/datefix:/data
    depends_on:
      - immich-server
```

If the GHCR package is private, log in once on the host:

```bash
echo $GITHUB_TOKEN | docker login ghcr.io -u ElPaul0 --password-stdin
```

Open `http://<host>:2284`, create a user (username + PIN + Immich API key), then scan / dry-run / apply. Later logins only need username + PIN.

API key permissions: `asset.read`, `asset.update`, and search/metadata as needed. User data lives in the `/data` volume (`users.json`, `sessions.json`).

## Dev

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# Linux:  source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8080
```

```bash
docker build -t immich-datefix:local .
docker run --rm -p 8080:8080 -e IMMICH_URL=http://host.docker.internal:2283 immich-datefix:local
```

## License

MIT — see [LICENSE](LICENSE).
