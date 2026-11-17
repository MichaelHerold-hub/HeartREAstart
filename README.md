# HeartREAstart

Erkennung des idealen Druckpunkts an einer Reanimationspuppe mit einer
**Intel RealSense Depth Camera D435f** und einem **corpuls-cpr-Modul**.

Das System erkennt die Puppe und den corpuls-cpr-Stempel im Livebild,
berechnet die Körperachse und blendet den zulässigen Druckbereich
(mittlere bis untere Sternumhälfte) als virtuelles Overlay ein. An der Puppe
selbst wird nichts markiert.

## Medizinischer Hintergrund

Der corpuls-cpr-Stempel soll **mittig in der unteren Hälfte des Sternums**
platziert werden, niemals auf oder unterhalb des Schwertfortsatzes
(Processus xiphoideus). Genau dieser Bereich wird als grüne Zone im
Livebild dargestellt.

## Funktionsweise

```text
RealSense D435f
      │ USB 3
      ▼
Rechner (z. B. Raspberry Pi 5)
      │
      ├─ RGB-Bild + Tiefenkarte erfassen
      ├─ Puppe erkennen (Kontur)
      ├─ corpuls-cpr-Stempel erkennen (Kanten)
      ├─ Körperachse berechnen (vertikale Mittellinie)
      ├─ virtuellen Druckbereich berechnen
      └─ Overlay im Livebild:
           "Position korrekt" / "Position prüfen"
```

## Hardware

- Intel RealSense Depth Camera D435f
- corpuls-cpr-Modul mit Stempel
- Reanimationspuppe
- Rechner mit USB 3 (getestet-Konfiguration: Raspberry Pi 5 oder PC)
- USB-3-Kabel (möglichst kurz und gut geschirmt)

## Installation

```bash
pip install -r requirements.txt
```

Zusätzlich wird das librealsense SDK (Version 2.x) benötigt, damit
`pyrealsense2` funktioniert. Auf dem Raspberry Pi 5 hat sich die
Installation aus dem Quellcode mit dem RSUSB-Backend bewährt:

```bash
# librealsense gemaess offizieller Anleitung bauen:
# https://github.com/realsenseai/librealsense
```

Prüfen, ob die Kamera erkannt wird:

```bash
realsense-viewer
```

## Start

```bash
python cpr_pressure_point.py
```

Beenden mit Taste `q` im Bildfenster.

## Kalibrierung

Die Parameter am Anfang von `cpr_pressure_point.py` müssen einmalig an die
eigene Puppe, Beleuchtung, Kameraposition und Stempelfarbe angepasst werden:

| Parameter | Bedeutung |
|---|---|
| `PUPPET_BRIGHTNESS_THRESHOLD` | Helligkeitsschwelle zur Puppenerkennung |
| `MIN_PUPPET_AREA` | Mindestfläche der Puppenkontur |
| `MIN_STAMP_AREA` | Mindestfläche des Stempels |
| `PRESSURE_ZONE_TOP_RATIO` | Oberer Rand des Druckbereichs (0 = Kopf, 1 = Fuß) |
| `PRESSURE_ZONE_BOTTOM_RATIO` | Unterer Rand, deutlich oberhalb des Xiphoids |
| `PRESSURE_ZONE_WIDTH_RATIO` | Breite des zulässigen Bereichs |

### Vorgehen

1. Puppe in der späteren Praxenposition aufbauen.
2. Kamera über dem Kopf der Puppe montieren (Sternum und Stempel sichtbar).
3. Programm starten und Livebild prüfen.
4. `PRESSURE_ZONE_TOP_RATIO` und `PRESSURE_ZONE_BOTTOM_RATIO` so verschieben,
   dass die grüne Zone über dem unteren Sternumdrittel liegt.
5. `PRESSURE_ZONE_WIDTH_RATIO` auf die Stempelbreite anpassen.
6. Stempel in die korrekte Position legen und prüfen, ob
   "Position korrekt" angezeigt wird.
7. Stempel bewusst falsch platzieren (zu hoch, zu tief, seitlich) und
   prüfen, ob "Position prüfen" erscheint.

## Aufbau des Programms

- `detect_puppet()` – erkennt die Puppe als Kontur
- `detect_stamp()` – erkennt den corpuls-cpr-Stempel über Kanten
- `compute_body_axis()` – berechnet die vertikale Körper-Mittellinie
- `compute_pressure_zone()` – berechnet den virtuellen Druckbereich
- `evaluate_position()` – prüft Stempelzentrum gegen den Druckbereich
- `draw_overlay()` – zeichnet das Livebild-Overlay
- `main()` – RealSense-Stream, Hauptschleife

## Bekannte Grenzen (erste Version)

- Die Puppenerkennung basiert auf einem Helligkeitsschwellwert; bei
  ähnlicher Hintergrundfarbe muss der Wert angepasst oder die Erkennung
  später auf KI (Segmentierung) erweitert werden.
- Die Stempelerkennung basiert auf Kanten; bei markanter Stempelfarbe ist
  eine HSV-Farbfilterung oft robuster.
- Der Druckbereich ist relativ zum erkannten Puppenbereich definiert; eine
  präzise anatomische Sternumerkennung per KI ist ein sinnvoller nächster
  Schritt.
- Die Tiefenkarte wird aktuell nur zur Kontrolle mit angezeigt; sie kann
  später zur Prüfung genutzt werden, ob der Stempel tatsächlich auf dem
  Thorax aufliegt.

## Geplante Erweiterungen

- HSV-Farbfilterung oder kleines YOLO-Modell für die Stempelerkennung
- KI-Segmentierung von Thorax und Sternum
- Tiefendaten zur Lage- und Auflageprüfung des Stempels
- Feedback per LED, Display oder Webinterface
- Aufzeichnung von Testbildern für die Weiterentwicklung

## Lizenz

Projektarbeit – Lizenz wird von den Projektbeteiligten festgelegt.
