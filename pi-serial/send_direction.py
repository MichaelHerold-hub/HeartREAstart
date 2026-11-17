#!/usr/bin/env python3
"""
HeartREAstart - Serielle Steuerung der Pfeilanzeige
====================================================

Sendet Richtungskommandos an die Firmware auf dem
Renesas YRPBRL78L12 (RL78/L12) ueber die serielle
Schnittstelle des Raspberry Pi 5.

Kommandos:
    u  -> Pfeil oben
    d  -> Pfeil unten
    l  -> Pfeil links
    r  -> Pfeil rechts
    c  -> alle Pfeile aus (Position korrekt)

Verkabelung:
    Pi TX (GPIO14)  -> RL78/L12 RX
    Pi GND          -> RL78/L12 GND

Baudrate: 9600, 8N1
"""

import serial
import time
import sys

# Serielle Schnittstelle auf dem Raspberry Pi 5
SERIAL_PORT = "/dev/ttyS0"
BAUDRATE = 9600
TIMEOUT = 1


def open_serial():
    """Oeffnet die serielle Verbindung zum RL78/L12."""
    try:
        ser = serial.Serial(
            SERIAL_PORT,
            BAUDRATE,
            bytesize=serial.EIGHTBITS,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            timeout=TIMEOUT
        )
        print(f"Serielle Verbindung geoeffnet: {SERIAL_PORT} @ {BAUDRATE} Baud")
        return ser
    except serial.SerialException as e:
        print(f"Fehler beim Oeffnen der seriellen Schnittstelle: {e}")
        sys.exit(1)


def send_direction(ser, direction):
    """Sendet ein Richtungskommando an den RL78/L12.

    direction: 'u', 'd', 'l', 'r' oder 'c'
    """
    if direction not in ("u", "d", "l", "r", "c"):
        print(f"Ungueltiges Kommando: {direction}")
        return

    ser.write(direction.encode("ascii"))
    print(f"Gesendet: {direction}")


def test_cycle(ser):
    """Sendet alle vier Richtungen nacheinander fuer Tests."""
    directions = ["u", "d", "l", "r", "c"]

    for d in directions:
        send_direction(ser, d)
        time.sleep(1.0)


def interactive_mode(ser):
    """Interaktive Eingabe von Richtungskommandos."""
    print("\nInteraktiver Modus.")
    print("Kommandos: u (oben), d (unten), l (links), r (rechts), c (aus)")
    print("Beenden mit 'q'.\n")

    while True:
        cmd = input("Kommando > ").strip().lower()

        if cmd == "q":
            print("Beende Programm.")
            break
        elif cmd in ("u", "d", "l", "r", "c"):
            send_direction(ser, cmd)
        else:
            print("Ungueltige Eingabe. Erlaubt: u, d, l, r, c, q")


def main():
    ser = open_serial()

    try:
        # Zuerst einen automatischen Testzyklus ausfuehren
        print("Starte automatischen Testzyklus...")
        test_cycle(ser)

        # Danach in den interaktiven Modus wechseln
        interactive_mode(ser)

    except KeyboardInterrupt:
        print("\nAbgebrochen durch Benutzer.")

    finally:
        ser.close()
        print("Serielle Verbindung geschlossen.")


if __name__ == "__main__":
    main()
