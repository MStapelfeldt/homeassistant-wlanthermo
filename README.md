# WLANThermo (ESP32) — Home Assistant Custom Integration

![Version](https://img.shields.io/badge/version-0.1.0-informational)
![License](https://img.shields.io/badge/license-MIT-green)
![Home%20Assistant](https://img.shields.io/badge/Home%20Assistant-2024%2B-blue)
![Support](https://img.shields.io/badge/support-No%20support%20provided-lightgrey)
![Owner](https://img.shields.io/badge/code%20owner-@lemuba-purple)

**Version:** 0.1.0  
**Code Owner:** @lemuba  
**Lizenz:** MIT

> **Hinweis & Haftungsausschluss**  
> Diese Integration wurde von **ChatGPT (Assistent)** für @lemuba erstellt.  
> **Der Repo-Inhaber bietet keinen Support** für diese Integration. Forks/Weiterentwicklung/Bugfixes sind ausdrücklich erwünscht.  
> **Keine Gewähr/Haftung** — Nutzung auf eigene Verantwortung.

## API-Referenz
Offizielle HTTP-API: https://github.com/WLANThermo-nano/WLANThermo_ESP32_Software/wiki/HTTP  
Routen **lowercase** verwenden (`/setpitmaster`, `/setchannels`, `/setpid`, `/setsystem`).  
**Pitmaster-Writes:** vollständige verschachtelte PM-Objekte im **Array** senden.

## Features
- **Nur Pitmaster 1** (Pitmaster 2 absichtlich entfernt).
- **Pitmaster 1 Output**-Sensor (Regelgröße in %).
- **Temperatur pro Kanal**: `<Kanalname> Temperature` **und** `Channel X Temperature` (fixer Name).
- **Channel Alarm**-Select, **Sensor Type**-Select, **Min/Max**-Numbers (−30…+350 °C).
- **Systemsensoren**: RSSI, Battery Level, Battery Charging.
- **Offline-toleranter Start** (Entitäten werden verfügbar, sobald das Gerät online ist).

## Manuelle Installation
1. Repo entpacken.  
2. `custom_components/wlanthermo` nach `<HA config>/custom_components/` kopieren.  
3. Home Assistant neu starten.

## Einrichtung
Einstellungen → Geräte & Dienste → **Integration hinzufügen** → **WLANThermo**. Host/Port (Default 80) und ggf. Auth angeben.

## Entitäten (Überblick)
- **Pitmaster 1**: Mode, Channel, Profile, Setpoint, Manual Output (Writes via `/setpitmaster`), **Sensor: Pitmaster 1 Output**.  
- **Kanäle 1–12**: `<Name> Temperature`, `Channel X Temperature`, Alarm-Select, Sensor-Type-Select, Min/Max-Number.  
- **System**: RSSI, Battery Level, Battery Charging.

## Screenshots

**Setup-Dialog**  
![Setup](docs/images/01-setup.jpg)

**Steuerelemente für Kanäle**  
![Channel Settings](docs/images/02-channel-settings.jpg)

**Pitmaster 1 Einstellungen**  
![Pitmaster Settings](docs/images/03-pitmaster-settings.jpg)

**Sensoren (Temperaturen, Output, RSSI, Battery)**  
![Sensors](docs/images/04-sensors.jpg)

**Geräteseite in Home Assistant**  
![Integration](docs/images/05-integration.jpg)

---

## English

This custom integration targets **WLANThermo ESP32** (Nano/Next) for **Home Assistant**.

**Attribution & Disclaimer**
- Created by **ChatGPT (Assistant)** for **@lemuba**.
- **No support** is provided by the repository owner. Forks and community-driven development/bugfixes are welcome.
- **No warranty/liability** — use at your own risk. License: **MIT**. Code owner: **@lemuba**.

**API Reference**
- Official HTTP API: https://github.com/WLANThermo-nano/WLANThermo_ESP32_Software/wiki/HTTP
- Use **lowercase** routes (`/setpitmaster`, `/setchannels`, `/setpid`, `/setsystem`).
- For **Pitmaster writes** send **complete nested** PM objects in an array.

**Features**
- **Pitmaster 1 only** (Pitmaster 2 intentionally removed).
- **Pitmaster 1 Output** sensor (%).
- Per-channel temperature sensors: `<Name> Temperature` and **fixed** `Channel X Temperature`.
- Channel Alarm select, Sensor Type select, Min/Max numbers (−30…+350 °C).
- System sensors: RSSI, Battery Level, Battery Charging.
- Offline-tolerant startup.

**Manual Installation**
1. Extract this repository.  
2. Copy `custom_components/wlanthermo` into `<HA config>/custom_components/`.  
3. Restart Home Assistant.

**Setup**
Settings → Devices & Services → **Add Integration** → **WLANThermo**. Provide host/port; credentials if required.
