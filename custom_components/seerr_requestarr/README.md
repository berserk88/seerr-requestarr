# Seerr Requestarr

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/hacs/integration)
[![Version](https://img.shields.io/badge/version-1.2.0-blue.svg)](https://github.com/berserk88/seerr-requestarr)

Home Assistant integration for [Overseerr](https://overseerr.dev/). Provides a backend API proxy, sensor entities, and HA services — required for the Seerr Requestarr Card.

> **Also install the card:** [seerr-requestarr-card](https://github.com/berserk88/seerr-requestarr-card)

---

## Installation via HACS

1. HACS → Integrations → ⋮ → Custom repositories
2. Add `https://github.com/berserk88/seerr-requestarr` → Category: **Integration**
3. Download → Restart Home Assistant
4. Settings → Devices & Services → Add Integration → **Seerr Requestarr**
5. Enter your Overseerr URL (e.g. `http://192.168.1.100:5055`) and API key
   - API key is in Overseerr → Settings → General

---

## How it works

The integration registers a backend HTTP proxy at `/api/seerr_proxy/{path}` on the Home Assistant server. The card calls this proxy instead of Overseerr directly, which:

- **Eliminates CORS issues** — no direct browser-to-Overseerr traffic
- **No credentials in card config** — the proxy uses the stored API key server-side
- **Works over HTTPS** — no mixed-content problems

A diagnostic endpoint at `/api/seerr_debug` confirms connectivity (HA login required).

---

## Sensors

| Entity | Description |
|---|---|
| `sensor.seerr_requestarr_pending` | Requests awaiting approval |
| `sensor.seerr_requestarr_total`   | Total all-time requests |

---

## Services

### `seerr_requestarr.request_media`
```yaml
service: seerr_requestarr.request_media
data:
  media_type: movie   # or tv
  media_id: 550       # TMDB ID
```

### `seerr_requestarr.search`
Fires an `seerr_requestarr_search_results` event on the HA event bus.
```yaml
service: seerr_requestarr.search
data:
  query: "The Bear"
```

---

## Automation example

```yaml
automation:
  - alias: "Seerr — Pending Request Alert"
    trigger:
      - platform: state
        entity_id: sensor.seerr_requestarr_pending
    condition:
      - condition: numeric_state
        entity_id: sensor.seerr_requestarr_pending
        above: 0
    action:
      - service: notify.mobile_app_your_phone
        data:
          title: "Seerr Requestarr"
          message: "{{ states('sensor.seerr_requestarr_pending') }} request(s) awaiting approval"
```

---

## Requirements

- Home Assistant 2023.1.0 or newer
- [Overseerr](https://overseerr.dev/) accessible from your HA server
