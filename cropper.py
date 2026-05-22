# cropper.py
# OpenCV-logik för Klippare – hittar motiv på bildark och sparar PNG. Klipparen är byggd av Hans Åberg och KlⒶsse Kod
# Senast uppdaterad: 2026-05-20 | av: KlⒶssⓔ & Ⓐberg

from pathlib import Path

import cv2
import numpy as np


BACKGROUND_COLORS = {
    # OpenCV använder BGR-ordning internt.
    "white": (255, 255, 255),
    "light_gray": (238, 238, 238),
    "black": (0, 0, 0),
}


def make_square_canvas(image, background_color="white"):
    """Lägg bilden centrerad på en kvadratisk canvas."""
    height, width = image.shape[:2]
    side = max(width, height)
    color = BACKGROUND_COLORS.get(background_color, BACKGROUND_COLORS["white"])

    canvas = np.full((side, side, 3), color, dtype=np.uint8)
    offset_x = (side - width) // 2
    offset_y = (side - height) // 2
    canvas[offset_y : offset_y + height, offset_x : offset_x + width] = image
    return canvas


def sort_boxes_reading_order(boxes):
    """Sortera rutor ungefär som man läser: rad för rad, vänster till höger."""
    if not boxes:
        return []

    median_height = int(np.median([box[3] for box in boxes])) or 1
    row_tolerance = max(12, median_height // 2)

    rows = []
    for box in sorted(boxes, key=lambda item: item[1]):
        x, y, width, height = box
        placed = False
        for row in rows:
            if abs(row["y"] - y) <= row_tolerance:
                row["boxes"].append(box)
                row["y"] = int((row["y"] + y) / 2)
                placed = True
                break
        if not placed:
            rows.append({"y": y, "boxes": [box]})

    ordered = []
    for row in sorted(rows, key=lambda item: item["y"]):
        ordered.extend(sorted(row["boxes"], key=lambda item: item[0]))
    return ordered


def find_icon_boxes(image, settings):
    """Skapa mask, hitta contours och returnera filtrerade bounding boxes."""
    threshold_value = int(settings["threshold_value"])
    min_area = int(settings["min_area"])
    morph_kernel = (
        max(1, int(settings["morph_close_kernel_w"])),
        max(1, int(settings["morph_close_kernel_h"])),
    )
    dilate_kernel = (
        max(1, int(settings["dilate_kernel_w"])),
        max(1, int(settings["dilate_kernel_h"])),
    )

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Ljusa ark får vit bakgrund. THRESH_BINARY_INV gör motivet vitt i masken.
    _, mask = cv2.threshold(gray, threshold_value, 255, cv2.THRESH_BINARY_INV)

    close_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, morph_kernel)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, close_kernel)

    dilate_kernel_matrix = cv2.getStructuringElement(cv2.MORPH_RECT, dilate_kernel)
    mask = cv2.dilate(mask, dilate_kernel_matrix, iterations=1)

    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    image_area = image.shape[0] * image.shape[1]
    max_area = image_area * 0.95
    boxes = []
    for contour in contours:
        area = cv2.contourArea(contour)
        if area < min_area or area > max_area:
            continue

        x, y, width, height = cv2.boundingRect(contour)
        if width <= 1 or height <= 1:
            continue
        boxes.append((x, y, width, height))

    return sort_boxes_reading_order(boxes)


def crop_icons_from_sheet(source_path, output_dir, job_name, start_index, settings):
    """Läs ett ark, beskär hittade motiv och spara dem som PNG-filer."""
    source_path = Path(source_path)
    output_dir = Path(output_dir)

    image = cv2.imread(str(source_path), cv2.IMREAD_COLOR)
    if image is None:
        raise ValueError(f"OpenCV kunde inte läsa bilden: {source_path.name}")

    boxes = find_icon_boxes(image, settings)
    if not boxes:
        raise ValueError(f"Inga objekt hittades i {source_path.name}.")

    padding = max(0, int(settings["padding"]))
    make_square = bool(settings.get("make_square"))
    background_color = settings.get("background_color", "white")
    image_height, image_width = image.shape[:2]

    saved_files = []
    for offset, (x, y, width, height) in enumerate(boxes, start=start_index):
        left = max(0, x - padding)
        top = max(0, y - padding)
        right = min(image_width, x + width + padding)
        bottom = min(image_height, y + height + padding)

        crop = image[top:bottom, left:right].copy()
        if make_square:
            crop = make_square_canvas(crop, background_color)

        filename = f"{job_name}_{offset:02d}.png"
        destination = output_dir / filename
        cv2.imwrite(str(destination), crop)
        saved_files.append(filename)

    return saved_files
