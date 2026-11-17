"""
HeartREAstart - Druckpunkt-Erkennung an einer Reanimationspuppe
================================================================

Erkennt mit einer Intel RealSense D435f die Puppe und den corpuls-cpr-Stempel,
berechnet die Koerperachse und blendet den zulaessigen Druckbereich
(mittlere bis untere Sternumhaelfte) als Overlay im Livebild ein.

Der Stempel wird als korrekt platziert bewertet, wenn sein Mittelpunkt
innerhalb des virtuellen Druckbereichs liegt.

Voraussetzungen:
    pip install pyrealsense2 opencv-python numpy

Start:
    python cpr_pressure_point.py

Beenden:
    Taste "q" im Bildfenster druecken.

Hinweise zur Kalibrierung:
    Die Parameter unter "KONFIGURATION" muessen einmalig an Puppe,
    Beleuchtung, Kameraposition und Stempelfarbe angepasst werden.
"""

import cv2
import numpy as np
import pyrealsense2 as rs

# ------------------------------------------------------------
# KONFIGURATION
# ------------------------------------------------------------
WIDTH = 848
HEIGHT = 480
FPS = 15

# Parameter der Puppenerkennung (Schwellwert-Helligkeit, 0-255)
PUPPET_BRIGHTNESS_THRESHOLD = 90
MIN_PUPPET_AREA = 20000          # Mindestflaeche der Puppenkontur in Pixeln

# Parameter der Stempelerkennung
MIN_STAMP_AREA = 1500            # Mindestflaeche des Stempels in Pixeln
STAMP_CANNY_LOW = 50             # Kanten-Erkennung: unterer Schwellwert
STAMP_CANNY_HIGH = 150           # Kanten-Erkennung: oberer Schwellwert

# Virtueller Druckbereich, relativ zum erkannten Puppenbereich:
#   - TOP_RATIO    : oberer Rand (0 = Kopfende, 1 = Fussende)
#   - BOTTOM_RATIO : unterer Rand, bleibt deutlich oberhalb des Xiphoids
#   - WIDTH_RATIO  : Breite des zulaessigen Bereichs relativ zur Puppenbreite
#
# Medizinische Zielvorgabe (corpuls / AHA):
# Stempel mittig in der unteren Sternumhaelfte platzieren,
# niemals auf oder unterhalb des Schwertfortsatzes (Processus xiphoideus).
PRESSURE_ZONE_TOP_RATIO = 0.52
PRESSURE_ZONE_BOTTOM_RATIO = 0.72
PRESSURE_ZONE_WIDTH_RATIO = 0.18

# Anzeige
WINDOW_NAME = "HeartREAstart - Druckpunkt-Erkennung"


# ------------------------------------------------------------
# HILFSFUNKTIONEN
# ------------------------------------------------------------
def detect_puppet(blurred_gray):
    """Erkennt die Puppe als groesste helle/dunkle Kontur im Bild.

    Rueckgabe: (bounding_box, contour) oder (None, None)
    bounding_box = (x, y, w, h)
    """
    # Puppe als dunkle Flaeche vor hellem Hintergrund:
    _, threshold = cv2.threshold(
        blurred_gray, PUPPET_BRIGHTNESS_THRESHOLD, 255, cv2.THRESH_BINARY_INV
    )

    contours, _ = cv2.findContours(
        threshold, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
    )

    best_contour = None
    best_box = None

    for contour in contours:
        area = cv2.contourArea(contour)
        if area < MIN_PUPPET_AREA:
            continue

        x, y, w, h = cv2.boundingRect(contour)

        # Puppe ist liegend laenger als breit -> im Bild hoeher als breit.
        if h < w:
            continue

        if best_box is None or area > cv2.contourArea(best_contour):
            best_contour = contour
            best_box = (x, y, w, h)

    return best_box, best_contour


def detect_stamp(blurred_gray, puppet_box):
    """Erkennt den corpuls-cpr-Stempel ueber Kantenerkennung.

    Rueckgabe: (stamp_box, stamp_center) oder (None, None)
    stamp_box = (x, y, w, h)
    stamp_center = (cx, cy)
    """
    edges = cv2.Canny(blurred_gray, STAMP_CANNY_LOW, STAMP_CANNY_HIGH)
    edges = cv2.dilate(edges, np.ones((3, 3), np.uint8), iterations=1)

    contours, _ = cv2.findContours(
        edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
    )

    best_box = None
    best_area = 0

    for contour in contours:
        area = cv2.contourArea(contour)
        if area < MIN_STAMP_AREA:
            continue

        x, y, w, h = cv2.boundingRect(contour)

        # Stempel muss innerhalb des erkannten Puppenbereichs liegen.
        if puppet_box is not None:
            px, py, pw, ph = puppet_box
            if not (px <= x and y >= py and x + w <= px + pw and y + h <= py + ph):
                continue

        if area > best_area:
            best_area = area
            best_box = (x, y, w, h)

    if best_box is None:
        return None, None

    x, y, w, h = best_box
    center = (int(x + w / 2), int(y + h / 2))
    return best_box, center


def compute_body_axis(puppet_box):
    """Berechnet die vertikale Koerper-Mittellinie der Puppe.

    Rueckgabe: ((x, y_oben), (x, y_unten)) oder None
    """
    if puppet_box is None:
        return None

    px, py, pw, ph = puppet_box
    axis_x = int(px + pw / 2)
    return ((axis_x, py), (axis_x, py + ph))


def compute_pressure_zone(puppet_box):
    """Berechnet den virtuellen Druckbereich (untere Sternumhaelfte).

    Rueckgabe: (x1, y1, x2, y2) oder None
    """
    if puppet_box is None:
        return None

    px, py, pw, ph = puppet_box

    zone_top = int(py + ph * PRESSURE_ZONE_TOP_RATIO)
    zone_bottom = int(py + ph * PRESSURE_ZONE_BOTTOM_RATIO)

    axis_x = int(px + pw / 2)
    zone_width = int(pw * PRESSURE_ZONE_WIDTH_RATIO)

    zone_left = axis_x - zone_width // 2
    zone_right = axis_x + zone_width // 2

    return (zone_left, zone_top, zone_right, zone_bottom)


def evaluate_position(stamp_center, pressure_zone):
    """Prueft, ob das Stempelzentrum im zulaessigen Bereich liegt.

    Rueckgabe: True / False / None (wenn Werte fehlen)
    """
    if stamp_center is None or pressure_zone is None:
        return None

    x1, y1, x2, y2 = pressure_zone
    sx, sy = stamp_center

    return x1 <= sx <= x2 and y1 <= sy <= y2


# ------------------------------------------------------------
# OVERLAY
# ------------------------------------------------------------
def draw_overlay(color_image, puppet_box, body_axis, pressure_zone,
                 stamp_box, stamp_center):
    """Zeichnet Puppe, Koerperachse, Druckbereich und Stempel ins Livebild."""
    overlay = color_image.copy()

    # Puppenbereich
    if puppet_box is not None:
        px, py, pw, ph = puppet_box
        cv2.rectangle(overlay, (px, py), (px + pw, py + ph), (255, 200, 0), 2)
        cv2.putText(
            overlay, "Puppe erkannt", (px, py - 10),
            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 200, 0), 2
        )

    # Koerperachse
    if body_axis is not None:
        cv2.line(overlay, body_axis[0], body_axis[1], (255, 0, 255), 2)

    # Virtueller Druckbereich
    if pressure_zone is not None:
        zx1, zy1, zx2, zy2 = pressure_zone
        cv2.rectangle(overlay, (zx1, zy1), (zx2, zy2), (0, 255, 0), 2)
        cv2.putText(
            overlay, "Zulaessiger Druckbereich", (zx1, zy1 - 10),
            cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 255, 0), 2
        )

    # corpuls-Stempel
    if stamp_box is not None and stamp_center is not None:
        sx, sy, sw, sh = stamp_box
        cv2.rectangle(overlay, (sx, sy), (sx + sw, sy + sh), (0, 165, 255), 2)
        cv2.circle(overlay, stamp_center, 6, (0, 0, 255), -1)
        cv2.putText(
            overlay, "corpuls-Stempel", (sx, sy - 10),
            cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 165, 255), 2
        )

    # Statusmeldung
    status = evaluate_position(stamp_center, pressure_zone)
    if status is not None:
        if status:
            text, color = "Position korrekt", (0, 255, 0)
        else:
            text, color = "Position pruefen", (0, 0, 255)

        cv2.putText(
            overlay, text, (20, 40),
            cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2
        )

    return overlay


# ------------------------------------------------------------
# HAUPTPROGRAMM
# ------------------------------------------------------------
def main():
    pipeline = rs.pipeline()
    config = rs.config()

    config.enable_stream(rs.stream.color, WIDTH, HEIGHT, rs.format.bgr8, FPS)
    config.enable_stream(rs.stream.depth, WIDTH, HEIGHT, rs.format.z16, FPS)

    profile = pipeline.start(config)

    # Tiefenkarte auf das Farbbild ausrichten,
    # damit RGB-Pixel direkt Tiefenwerten zugeordnet werden koennen.
    align = rs.align(rs.stream.color)

    print("HeartREAstart gestartet. Beenden mit Taste 'q'.")
    print("Hinweis: Parameter unter 'KONFIGURATION' ggf. an die eigene")
    print("Puppe, Beleuchtung und Kameraposition anpassen.")

    try:
        while True:
            frames = pipeline.wait_for_frames()
            aligned_frames = align.process(frames)

            color_frame = aligned_frames.get_color_frame()
            depth_frame = aligned_frames.get_depth_frame()

            if not color_frame or not depth_frame:
                continue

            color_image = np.asanyarray(color_frame.get_data())
            depth_image = np.asanyarray(depth_frame.get_data())

            # --- Bildvorverarbeitung ---
            gray = cv2.cvtColor(color_image, cv2.COLOR_BGR2GRAY)
            blurred = cv2.GaussianBlur(gray, (7, 7), 0)

            # --- Erkennung ---
            puppet_box, _ = detect_puppet(blurred)
            stamp_box, stamp_center = detect_stamp(blurred, puppet_box)
            body_axis = compute_body_axis(puppet_box)
            pressure_zone = compute_pressure_zone(puppet_box)

            # --- Overlay zeichnen ---
            overlay = draw_overlay(
                color_image, puppet_box, body_axis, pressure_zone,
                stamp_box, stamp_center
            )

            # --- Tiefenkarte zur Kontrolle mit anzeigen ---
            depth_colormap = cv2.applyColorMap(
                cv2.convertScaleAbs(depth_image, alpha=0.03),
                cv2.COLORMAP_JET
            )

            combined = np.hstack((overlay, depth_colormap))

            cv2.imshow(WINDOW_NAME, combined)

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

    finally:
        pipeline.stop()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
