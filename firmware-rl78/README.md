# Firmware RL78/L12 - Pfeil-Testprogramm

Firmware fuer die **Renesas YRPBRL78L12 Promotion Board** (RL78/L12,
R5F10RLC) zur Anzeige von vier Richtungspfeilen (oben, unten, links,
rechts) auf dem segmentierten LCD.

## Funktionen

1. **Automatischer Testmodus:** Die vier Pfeile werden zyklisch fuer
   je 1 Sekunde angezeigt (3 vollstaendige Zyklen).
2. **UART-Modus:** Danach wartet das Programm auf serielle
   Kommandos vom Raspberry Pi:

| Kommando | Anzeige            |
|----------|--------------------|
| `u` / `U`| Pfeil oben         |
| `d` / `D`| Pfeil unten        |
| `l` / `L`| Pfeil links        |
| `r` / `R`| Pfeil rechts       |
| `c` / `C`| Alle Pfeile aus (Position korrekt) |

## Voraussetzungen

- Renesas **e2 studio** (kostenlos, Download von renesas.com)
- **GCC fuer RL78** (CC-RL), kostenlos, in e2 studio integrierbar
- YRPBRL78L12 Promotion Board mit USB-Kabel
- Debuggen/Flashen ueber den **On-Chip-Debugger (OCD)** des Boards

## Installation

1. **e2 studio** installieren.
2. Neues RL78/L12-Projekt anlegen (Toolchain: GCC fuer RL78).
3. Die Datei `lcd_arrow_test.c` in das Projekt einfuegen.
4. **WICHTIG:** Die Platzhalter unter `SEGTXT-MAPPING (ANPASSEN)`
   im Quellcode an die tatsaechliche Segment-Belegung des
   YRPBRL78L12 anpassen. Quelle:
   - YRPBRL78L12 User's Manual (Rev.1.00)
   - RPBRL78L12 Renesas Promotion Board Schematics (Rev.1.00)
   - RL78/L12 User's Manual: Hardware (R01UH0200)
5. Projekt kompilieren und ueber den OCD auf das Board flashen.

## Segment-Mapping anpassen

Im Quellcode sind folgende Konstanten als **Platzhalter** definiert
und muessen ersetzt werden:

```c
static volatile uint8_t *LCD_SEG_BASE = (volatile uint8_t *)0xF0080u;

static const arrow_segment_t ARROW_UP    = { ..., 0x01u };
static const arrow_segment_t ARROW_DOWN  = { ..., 0x02u };
static const arrow_segment_t ARROW_LEFT  = { ..., 0x04u };
static const arrow_segment_t ARROW_RIGHT = { ..., 0x08u };
```

Die tatsaechlichen Registeradressen und Bit-Masken entnehmt ihr der
**Segment-Tabelle** im YRPBRL78L12 User's Manual bzw. dem Schaltplan.

## UART-Verkabelung (Raspberry Pi 5 <-> RL78/L12)

| Raspberry Pi 5 | RL78/L12 (YRPBRL78L12) |
|----------------|------------------------|
| TX (GPIO14)    | RX (UART-Eingang)       |
| GND            | GND                    |

Beide Boards arbeiten mit 3,3-V-Logik, daher ist keine
Pegelwandlung noetig. Die Baudrate betraegt 9600, 8N1.

## Python-Beispiel (Raspberry Pi)

```python
import serial

ser = serial.Serial("/dev/ttyS0", 9600, timeout=1)

# Pfeil nach links anzeigen:
ser.write(b"l")

# Position korrekt:
ser.write(b"c")
```

## Referenzen

- Renesas YRPBRL78L12 Evaluation Board:
  https://www.renesas.com/en/design-resources/boards-kits/yrpbrl78l12
- RL78/L12 User's Manual: Hardware (R01UH0200):
  https://www.renesas.com/en/document/man/rl78g12-users-manual-hardware-0
- YRPBRL78L12 User's Manual (Rev.1.00):
  https://www.renesas.com/en/design-resources/boards-kits/yrpbrl78l12
