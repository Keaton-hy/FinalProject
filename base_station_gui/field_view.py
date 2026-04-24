from __future__ import annotations

from dataclasses import dataclass
import math
import tkinter as tk


@dataclass
class Pose:
    x_cm: float = 0.0
    y_cm: float = 0.0
    heading_deg: float = 90.0


@dataclass
class Detection:
    angle_deg: float
    distance_cm: float
    label: str


class FieldView(tk.Canvas):
    def __init__(self, master: tk.Misc) -> None:
        super().__init__(
            master,
            background="#2a1813",
            highlightthickness=1,
            highlightbackground="#7d4a35",
        )
        self.pose = Pose()
        self.scale_px_per_cm = 3.0
        self.detections: list[Detection] = []
        self.bind("<Configure>", lambda _: self.redraw())

    def reset_scan(self) -> None:
        self.detections.clear()
        self.redraw()

    def add_detection(self, angle_deg: float, distance_cm: float, label: str) -> None:
        self.detections.append(Detection(angle_deg=angle_deg, distance_cm=distance_cm, label=label))
        self.redraw()

    def apply_odometry(self, distance_mm: float, angle_deg: float) -> None:
        self.pose.heading_deg = (self.pose.heading_deg + angle_deg) % 360
        self._move(distance_mm / 10.0)
        self.redraw()

    def note_command(self, command: str) -> None:
        if command == "forward":
            self._move(1)
        elif command == "backward":
            self._move(-1)
        elif command == "left":
            self.pose.heading_deg = (self.pose.heading_deg + 2.5) % 360
        elif command == "right":
            self.pose.heading_deg = (self.pose.heading_deg - 2.5) % 360
        elif command == "forward_left":
            self.pose.heading_deg = (self.pose.heading_deg + 1.25) % 360
            self._move(1)
        elif command == "forward_right":
            self.pose.heading_deg = (self.pose.heading_deg - 1.25) % 360
            self._move(1)
        elif command == "backward_left":
            self.pose.heading_deg = (self.pose.heading_deg - 1.25) % 360
            self._move(-1)
        elif command == "backward_right":
            self.pose.heading_deg = (self.pose.heading_deg + 1.25) % 360
            self._move(-1)
        self.redraw()

    def redraw(self) -> None:
        self.delete("all")
        width = max(self.winfo_width(), 1)
        height = max(self.winfo_height(), 1)
        origin_x = width / 2
        origin_y = height / 2

        self._draw_grid(width, height, origin_x, origin_y)
        self._draw_scan_fan(origin_x, origin_y)
        for detection in self.detections:
            self._draw_detection(origin_x, origin_y, detection)
        self._draw_robot(origin_x, origin_y)

    def _move(self, distance_cm: float) -> None:
        radians = math.radians(self.pose.heading_deg)
        self.pose.x_cm += math.cos(radians) * distance_cm
        self.pose.y_cm += math.sin(radians) * distance_cm

    def _world_to_canvas(self, origin_x: float, origin_y: float, x_cm: float, y_cm: float) -> tuple[float, float]:
        return (
            origin_x + x_cm * self.scale_px_per_cm,
            origin_y - y_cm * self.scale_px_per_cm,
        )

    def _scan_to_world(self, angle_deg: float, distance_cm: float) -> tuple[float, float]:
        relative_deg = angle_deg - 90.0
        absolute_deg = self.pose.heading_deg + relative_deg
        radians = math.radians(absolute_deg)
        return (
            self.pose.x_cm + math.cos(radians) * distance_cm,
            self.pose.y_cm + math.sin(radians) * distance_cm,
        )

    def _draw_grid(self, width: int, height: int, origin_x: float, origin_y: float) -> None:
        spacing = 30
        for x in range(int(origin_x % spacing), width, spacing):
            self.create_line(x, 0, x, height, fill="#3a2119")
        for y in range(int(origin_y % spacing), height, spacing):
            self.create_line(0, y, width, y, fill="#3a2119")
        self.create_line(origin_x, 0, origin_x, height, fill="#7d4a35")
        self.create_line(0, origin_y, width, origin_y, fill="#7d4a35")

        self.create_text(
            14,
            14,
            text="MARS TERRAIN MAP",
            anchor="nw",
            fill="#d6a46b",
            font=("Segoe UI", 10, "bold"),
        )

    def _draw_scan_fan(self, origin_x: float, origin_y: float) -> None:
        x, y = self._world_to_canvas(origin_x, origin_y, self.pose.x_cm, self.pose.y_cm)
        radius = 65 * self.scale_px_per_cm
        self.create_arc(
            x - radius,
            y - radius,
            x + radius,
            y + radius,
            start=self.pose.heading_deg - 90,
            extent=180,
            outline="#66c6d0",
            style="arc",
            width=2,
        )

    def _draw_detection(self, origin_x: float, origin_y: float, detection: Detection) -> None:
        world_x, world_y = self._scan_to_world(detection.angle_deg, detection.distance_cm)
        x, y = self._world_to_canvas(origin_x, origin_y, world_x, world_y)
        self.create_line(
            *self._world_to_canvas(origin_x, origin_y, self.pose.x_cm, self.pose.y_cm),
            x,
            y,
            fill="#5a8f91",
            dash=(3, 4),
        )
        self.create_oval(x - 6, y - 6, x + 6, y + 6, fill="#ffcf70", outline="#f36f45", width=2)
        self.create_text(x + 9, y - 9, text=detection.label, anchor="sw", fill="#ffd99d", font=("Segoe UI", 8, "bold"))

    def _draw_robot(self, origin_x: float, origin_y: float) -> None:
        x, y = self._world_to_canvas(origin_x, origin_y, self.pose.x_cm, self.pose.y_cm)
        heading = math.radians(self.pose.heading_deg)
        left = heading + math.radians(140)
        right = heading - math.radians(140)
        nose = (x + math.cos(heading) * 16, y - math.sin(heading) * 16)
        rear_left = (x + math.cos(left) * 12, y - math.sin(left) * 12)
        rear_right = (x + math.cos(right) * 12, y - math.sin(right) * 12)
        self.create_oval(x - 11, y - 11, x + 11, y + 11, fill="#162426", outline="#66c6d0", width=2)
        self.create_polygon(*nose, *rear_left, *rear_right, fill="#62d0d7", outline="#dffcff", width=2)
        self.create_text(x, y + 24, text="CYBOT", fill="#bff6f8", font=("Segoe UI", 9, "bold"))
