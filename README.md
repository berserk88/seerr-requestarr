# Seerr Requestarr

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/hacs/integration)

Home Assistant integration for [Overseerr](https://overseerr.dev/) — registers a backend proxy endpoint used by the Seerr Requestarr Card, plus sensor entities and HA services.

> **Also install the card:** [seerr-requestarr-card](https://github.com/berserk88/seerr-requestarr-card)

---

## Installation via HACS

1. HACS → Integrations → ⋮ → Custom repositories
2. Add `https://github.com/berserk88/seerr-requestarr` → Category: **Integration**
3. Download → Restart HA
4. Settings → Devices & Services → Add Integration → **Seerr Requestarr**
5. Enter your Overseerr URL and API key (Settings → General in Overseerr)

---

## Diagnostics

Visit `http://YOUR_HA_IP:8123/api/seerr_debug` (requires HA login) to verify the proxy is working and Overseerr is reachable.

---

## Sensors

| Entity | Description |
|---|---|
| `sensor.seerr_requestarr_pending` | Pending requests |
| `sensor.seerr_requestarr_total`   | Total requests   |

---

## Services

### `seerr_requestarr.request_media`
```yaml
service: seerr_requestarr.request_media
data:
  media_type: movie   # or tv
  media_id: 550
```
