from __future__ import annotations

import queue
import tkinter as tk
from tkinter import ttk

from .connection import CyBotConnection
from .field_view import FieldView
from .protocol import DEFAULT_HOST, DEFAULT_PORT, ObjectReading, OIStatus, PingReading, RawLine, parse_line


DRIVE_COMMANDS = {
    "forward",
    "backward",
    "left",
    "right",
    "forward_left",
    "forward_right",
    "backward_left",
    "backward_right",
}


class BaseStationApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("Ares CyBot Command Station")
        self.geometry("1100x720")
        self.minsize(940, 600)
        self.configure(background="#171412")

        self.events: queue.Queue[tuple[str, str]] = queue.Queue()
        self.connection = CyBotConnection(
            on_line=lambda line: self.events.put(("line", line)),
            on_status=lambda status: self.events.put(("status", status)),
        )

        self.host_var = tk.StringVar(value=DEFAULT_HOST)
        self.port_var = tk.IntVar(value=DEFAULT_PORT)
        self.status_var = tk.StringVar(value="Disconnected")
        self.ping_var = tk.StringVar(value="--")
        self.last_object_var = tk.StringVar(value="--")
        self.oi_status_var = tk.StringVar(value="--")
        self.raw_command_var = tk.StringVar()
        self.simulated_line_var = tk.StringVar(value="Object 1:  90  42.00  8.00")
        self.active_drive_command: str | None = None
        self.drive_after_id: str | None = None
        self.drive_interval_ms = 50
        self.speed_var = tk.IntVar(value=100)
        self.pressed_drive_keys: set[str] = set()
        self.speed_after_id: str | None = None
        self.status_after_id: str | None = None
        self.last_sent_speed = self.speed_var.get()

        self._configure_styles()
        self._build_ui()
        self._bind_keys()
        self.after(50, self._process_events)

    def _configure_styles(self) -> None:
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure(".", background="#171412", foreground="#f3ddc0", font=("Segoe UI", 10))
        style.configure("TFrame", background="#171412")
        style.configure("Panel.TFrame", background="#241b18")
        style.configure("TLabel", background="#171412", foreground="#f3ddc0")
        style.configure("Title.TLabel", font=("Segoe UI", 18, "bold"), foreground="#ffcf70")
        style.configure("Subtle.TLabel", foreground="#c7956c")
        style.configure("Metric.TLabel", font=("Consolas", 13, "bold"), foreground="#73d7df", background="#241b18")
        style.configure("TLabelframe", background="#171412", bordercolor="#7d4a35", relief="solid")
        style.configure("TLabelframe.Label", background="#171412", foreground="#ffcf70", font=("Segoe UI", 10, "bold"))
        style.configure("TEntry", fieldbackground="#100d0c", foreground="#f3ddc0", bordercolor="#7d4a35")
        style.configure("TButton", background="#6f3828", foreground="#fff2df", bordercolor="#9a5a3e", padding=(10, 7))
        style.map("TButton", background=[("active", "#9b4e35"), ("pressed", "#d36f43")])
        style.configure("Drive.TButton", background="#254f55", foreground="#e5feff", padding=(12, 9), font=("Segoe UI", 10, "bold"))
        style.map("Drive.TButton", background=[("active", "#34727a"), ("pressed", "#66c6d0")])
        style.configure("Stop.TButton", background="#8f2f2f", foreground="#fff0e8", padding=(12, 9), font=("Segoe UI", 10, "bold"))
        style.map("Stop.TButton", background=[("active", "#b53e3e"), ("pressed", "#ff6b4a")])

    def _build_ui(self) -> None:
        self.columnconfigure(0, weight=0)
        self.columnconfigure(1, weight=1)
        self.rowconfigure(1, weight=1)

        top = ttk.Frame(self, padding=8)
        top.grid(row=0, column=0, columnspan=2, sticky="ew")
        top.columnconfigure(8, weight=1)

        ttk.Label(top, text="ARES CYBOT COMMAND", style="Title.TLabel").grid(row=0, column=0, columnspan=2, sticky="w", padx=(0, 22))
        ttk.Label(top, text="Host", style="Subtle.TLabel").grid(row=0, column=2, sticky="w")
        ttk.Entry(top, textvariable=self.host_var, width=16).grid(row=0, column=3, padx=(4, 12))
        ttk.Label(top, text="Port", style="Subtle.TLabel").grid(row=0, column=4, sticky="w")
        ttk.Entry(top, textvariable=self.port_var, width=6).grid(row=0, column=5, padx=(4, 12))
        ttk.Button(top, text="Connect", command=self._connect).grid(row=0, column=6, padx=(0, 6))
        ttk.Button(top, text="Disconnect", command=self.connection.disconnect).grid(row=0, column=7)
        ttk.Label(top, textvariable=self.status_var, style="Subtle.TLabel").grid(row=0, column=8, sticky="e")

        controls = ttk.LabelFrame(self, text="Controls", padding=12)
        controls.grid(row=1, column=0, sticky="nsw", padx=8, pady=8)

        self._hold_button(controls, "Forward", "forward").grid(row=0, column=1, padx=4, pady=4)
        self._hold_button(controls, "Left", "left").grid(row=1, column=0, padx=4, pady=4)
        ttk.Button(controls, text="Stop", style="Stop.TButton", command=lambda: self._stop_drive(force=True)).grid(row=1, column=1, padx=4, pady=4)
        self._hold_button(controls, "Right", "right").grid(row=1, column=2, padx=4, pady=4)
        self._hold_button(controls, "Backward", "backward").grid(row=2, column=1, padx=4, pady=4)

        speed = ttk.LabelFrame(controls, text="Speed", padding=8)
        speed.grid(row=3, column=0, columnspan=3, sticky="ew", pady=(12, 0))
        speed.columnconfigure(0, weight=1)
        ttk.Scale(speed, from_=50, to=250, variable=self.speed_var, command=self._speed_changed).grid(row=0, column=0, sticky="ew")
        self.speed_label = ttk.Label(speed, text="100 mm/s", style="Metric.TLabel")
        self.speed_label.grid(row=1, column=0, sticky="ew", pady=(4, 0))

        ttk.Separator(controls, orient="horizontal").grid(row=4, column=0, columnspan=3, sticky="ew", pady=12)
        ttk.Button(controls, text="Ping", command=lambda: self._send("ping")).grid(row=5, column=0, columnspan=3, sticky="ew", pady=4)
        ttk.Button(controls, text="Sweep", command=lambda: self._send("sweep")).grid(row=6, column=0, columnspan=3, sticky="ew", pady=4)
        ttk.Button(controls, text="OI Status", command=lambda: self._send("oi_status")).grid(row=7, column=0, columnspan=3, sticky="ew", pady=4)
        ttk.Button(controls, text="Wheel Test", command=lambda: self._send("wheel_test")).grid(row=8, column=0, columnspan=3, sticky="ew", pady=4)
        ttk.Button(controls, text="Standby", command=lambda: self._send("standby")).grid(row=9, column=0, columnspan=3, sticky="ew", pady=4)
        ttk.Button(controls, text="Reset Field", command=self._reset_field).grid(row=10, column=0, columnspan=3, sticky="ew", pady=(16, 4))
        ttk.Button(controls, text="Clear Log", command=self._clear_log).grid(row=11, column=0, columnspan=3, sticky="ew", pady=4)

        raw = ttk.LabelFrame(controls, text="Raw Test", padding=8)
        raw.grid(row=12, column=0, columnspan=3, sticky="ew", pady=(16, 0))
        raw.columnconfigure(0, weight=1)
        ttk.Entry(raw, textvariable=self.raw_command_var, width=12).grid(row=0, column=0, sticky="ew", pady=(0, 4))
        ttk.Button(raw, text="Send", command=self._send_raw).grid(row=0, column=1, padx=(4, 0), pady=(0, 4))
        ttk.Entry(raw, textvariable=self.simulated_line_var, width=18).grid(row=1, column=0, sticky="ew")
        ttk.Button(raw, text="Sim", command=self._simulate_line).grid(row=1, column=1, padx=(4, 0))

        telemetry = ttk.LabelFrame(self, text="Telemetry", padding=12)
        telemetry.grid(row=1, column=1, sticky="nsew", padx=(0, 8), pady=8)
        telemetry.columnconfigure(0, weight=1)
        telemetry.rowconfigure(3, weight=1)
        telemetry.rowconfigure(5, weight=1)

        stats = ttk.Frame(telemetry)
        stats.grid(row=0, column=0, sticky="ew")
        stats.columnconfigure(1, weight=1)

        ttk.Label(stats, text="Last ping", style="Subtle.TLabel").grid(row=0, column=0, sticky="w")
        ttk.Label(stats, textvariable=self.ping_var, style="Metric.TLabel").grid(row=0, column=1, sticky="w", padx=(8, 24))
        ttk.Label(stats, text="Last object", style="Subtle.TLabel").grid(row=1, column=0, sticky="w")
        ttk.Label(stats, textvariable=self.last_object_var, style="Metric.TLabel").grid(row=1, column=1, sticky="w", padx=(8, 24))
        ttk.Label(stats, text="OI status", style="Subtle.TLabel").grid(row=2, column=0, sticky="w")
        ttk.Label(stats, textvariable=self.oi_status_var, style="Metric.TLabel").grid(row=2, column=1, sticky="w", padx=(8, 24))

        ttk.Label(telemetry, text="Test Field").grid(row=2, column=0, sticky="w", pady=(16, 4))
        self.field = FieldView(telemetry)
        self.field.grid(row=3, column=0, sticky="nsew")

        ttk.Label(telemetry, text="Event Log").grid(row=4, column=0, sticky="w", pady=(16, 4))
        self.log = tk.Text(telemetry, height=8, wrap="word", state="disabled")
        self.log.configure(
            background="#100d0c",
            foreground="#f3ddc0",
            insertbackground="#ffcf70",
            relief="flat",
            borderwidth=8,
            font=("Consolas", 9),
        )
        self.log.grid(row=5, column=0, sticky="nsew")

    def _bind_keys(self) -> None:
        self.bind("<KeyPress-w>", lambda _: self._key_down("w"))
        self.bind("<KeyPress-s>", lambda _: self._key_down("s"))
        self.bind("<KeyPress-a>", lambda _: self._key_down("a"))
        self.bind("<KeyPress-d>", lambda _: self._key_down("d"))
        self.bind("<KeyRelease-w>", lambda _: self._key_up("w"))
        self.bind("<KeyRelease-s>", lambda _: self._key_up("s"))
        self.bind("<KeyRelease-a>", lambda _: self._key_up("a"))
        self.bind("<KeyRelease-d>", lambda _: self._key_up("d"))
        self.bind("<space>", lambda _: self._stop_drive(force=True))
        self.bind("<FocusOut>", lambda _: self._stop_drive())

    def _hold_button(self, master: tk.Misc, label: str, command: str) -> ttk.Button:
        button = ttk.Button(master, text=label, style="Drive.TButton")
        button.bind("<ButtonPress-1>", lambda _: self._start_drive(command))
        button.bind("<ButtonRelease-1>", lambda _: self._stop_drive())
        button.bind("<Leave>", lambda _: self._stop_drive())
        return button

    def _connect(self) -> None:
        self.connection.host = self.host_var.get().strip()
        self.connection.port = int(self.port_var.get())
        try:
            self.connection.connect()
        except OSError as exc:
            self._set_status(f"Connect failed: {exc}")

    def _send(self, command: str, report: bool = True) -> None:
        self.connection.send_command(command, report=report)
        self.field.note_command(command)
        if command in {"ping", "sweep"}:
            self.field.reset_scan()
        if command not in DRIVE_COMMANDS and command != "oi_status":
            self._schedule_status_check()

    def _speed_changed(self, _: str) -> None:
        speed = self.speed_var.get()
        self.speed_label.configure(text=f"{speed} mm/s")
        if self.speed_after_id is not None:
            self.after_cancel(self.speed_after_id)
        self.speed_after_id = self.after(120, self._send_speed)

    def _send_speed(self) -> None:
        self.speed_after_id = None
        speed = self.speed_var.get()
        if speed == self.last_sent_speed:
            return
        self.last_sent_speed = speed
        if self.connection.connected:
            self.connection.send_command(f"v{speed}", report=True)
            self._schedule_status_check(200)

    def _schedule_status_check(self, delay_ms: int = 150) -> None:
        if self.status_after_id is not None:
            self.after_cancel(self.status_after_id)
        self.status_after_id = self.after(delay_ms, self._send_status_check)

    def _send_status_check(self) -> None:
        self.status_after_id = None
        if self.connection.connected:
            self.connection.send_command("oi_status", report=False)

    def _key_down(self, key: str) -> None:
        self.pressed_drive_keys.add(key)
        command = self._command_from_keys()
        if command is not None:
            self._start_drive(command)

    def _key_up(self, key: str) -> None:
        self.pressed_drive_keys.discard(key)
        command = self._command_from_keys()
        if command is None:
            self._stop_drive()
        else:
            self._start_drive(command)

    def _command_from_keys(self) -> str | None:
        keys = self.pressed_drive_keys
        if "w" in keys and "a" in keys:
            return "forward_left"
        if "w" in keys and "d" in keys:
            return "forward_right"
        if "s" in keys and "a" in keys:
            return "backward_left"
        if "s" in keys and "d" in keys:
            return "backward_right"
        if "w" in keys:
            return "forward"
        if "s" in keys:
            return "backward"
        if "a" in keys:
            return "left"
        if "d" in keys:
            return "right"
        return None

    def _start_drive(self, command: str) -> None:
        if self.active_drive_command == command:
            return
        self._cancel_drive_tick()
        self.active_drive_command = command
        self._send(command)
        self.drive_after_id = self.after(self.drive_interval_ms, self._drive_tick)

    def _drive_tick(self) -> None:
        command = self.active_drive_command
        if command is None:
            self.drive_after_id = None
            return
        self._send(command, report=False)
        self.drive_after_id = self.after(self.drive_interval_ms, self._drive_tick)

    def _stop_drive(self, force: bool = False) -> None:
        was_driving = self.active_drive_command is not None
        self.pressed_drive_keys.clear()
        self.active_drive_command = None
        self._cancel_drive_tick()
        if was_driving or force:
            self.connection.send_command("stop")
            self._schedule_status_check(150)

    def _cancel_drive_tick(self) -> None:
        if self.drive_after_id is not None:
            self.after_cancel(self.drive_after_id)
            self.drive_after_id = None

    def _send_raw(self) -> None:
        command = self.raw_command_var.get()
        if not command:
            return
        if command.startswith("v") and command[1:].isdigit():
            self.connection.send_command(command)
            self.raw_command_var.set("")
            return
        for char in command:
            self.connection.send_command(char)
        self.raw_command_var.set("")

    def _simulate_line(self) -> None:
        line = self.simulated_line_var.get().strip()
        if line:
            self._handle_line(line)

    def _reset_field(self) -> None:
        self.field.pose.x_cm = 0
        self.field.pose.y_cm = 0
        self.field.pose.heading_deg = 90
        self.field.reset_scan()
        self._append_log("Field reset")

    def _clear_log(self) -> None:
        self.log.configure(state="normal")
        self.log.delete("1.0", "end")
        self.log.configure(state="disabled")

    def _process_events(self) -> None:
        while True:
            try:
                event_type, payload = self.events.get_nowait()
            except queue.Empty:
                break

            if event_type == "status":
                self._set_status(payload)
                self._append_log(payload)
            elif event_type == "line":
                self._handle_line(payload)

        self.after(50, self._process_events)

    def _handle_line(self, line: str) -> None:
        parsed = parse_line(line)
        if isinstance(parsed, PingReading):
            self.ping_var.set(f"{parsed.distance_cm:.2f} cm")
            self.field.add_detection(90, parsed.distance_cm, "Ping")
        elif isinstance(parsed, ObjectReading):
            self.last_object_var.set(
                f"#{parsed.object_num} at {parsed.angle_deg} deg, "
                f"{parsed.distance_cm:.2f} cm, width {parsed.radial_width:.2f}"
            )
            self.field.add_detection(
                parsed.angle_deg,
                parsed.distance_cm,
                f"Obj {parsed.object_num}",
            )
        elif isinstance(parsed, OIStatus):
            flags = []
            if parsed.bump_left or parsed.bump_right:
                flags.append("BUMP")
            if parsed.cliff_left or parsed.cliff_front_left or parsed.cliff_front_right or parsed.cliff_right:
                flags.append("CLIFF")
            flag_text = ", ".join(flags) if flags else "clear"
            self.oi_status_var.set(f"{flag_text}; d={parsed.distance_mm:.1f} mm a={parsed.angle_deg:.1f} deg")
            self.field.apply_odometry(parsed.distance_mm, parsed.angle_deg)
        elif isinstance(parsed, RawLine):
            pass

        self._append_log(line)

    def _set_status(self, message: str) -> None:
        self.status_var.set(message)

    def _append_log(self, message: str) -> None:
        self.log.configure(state="normal")
        self.log.insert("end", message + "\n")
        self.log.see("end")
        self.log.configure(state="disabled")


def main() -> None:
    app = BaseStationApp()
    app.mainloop()
