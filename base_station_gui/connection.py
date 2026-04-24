from __future__ import annotations

from collections.abc import Callable
import socket
import threading

from .protocol import DEFAULT_HOST, DEFAULT_PORT, encode_command


LineHandler = Callable[[str], None]
StatusHandler = Callable[[str], None]


class CyBotConnection:
    def __init__(
        self,
        on_line: LineHandler,
        on_status: StatusHandler,
        host: str = DEFAULT_HOST,
        port: int = DEFAULT_PORT,
    ) -> None:
        self.host = host
        self.port = port
        self._on_line = on_line
        self._on_status = on_status
        self._sock: socket.socket | None = None
        self._reader: threading.Thread | None = None
        self._stop = threading.Event()
        self._send_lock = threading.Lock()

    @property
    def connected(self) -> bool:
        return self._sock is not None

    def connect(self) -> None:
        if self._sock is not None:
            return

        sock = socket.create_connection((self.host, self.port), timeout=5)
        sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        sock.settimeout(0.25)
        self._sock = sock
        self._stop.clear()
        self._reader = threading.Thread(target=self._read_loop, daemon=True)
        self._reader.start()
        local_host, local_port = sock.getsockname()
        self._on_status(f"Connected {local_host}:{local_port} -> {self.host}:{self.port}")

    def disconnect(self) -> None:
        self._stop.set()
        sock = self._sock
        self._sock = None
        if sock is not None:
            try:
                sock.shutdown(socket.SHUT_RDWR)
            except OSError:
                pass
            sock.close()
        self._on_status("Disconnected")

    def send_command(self, command: str, report: bool = True) -> None:
        sock = self._sock
        if sock is None:
            if report:
                self._on_status("Not connected")
            return

        payload = encode_command(command)
        with self._send_lock:
            sock.sendall(payload)
        if report:
            self._on_status(f"Sent {payload.decode('ascii').strip()}")

    def _read_loop(self) -> None:
        buffer = b""
        while not self._stop.is_set():
            sock = self._sock
            if sock is None:
                return

            try:
                chunk = sock.recv(1024)
            except TimeoutError:
                continue
            except OSError as exc:
                if not self._stop.is_set():
                    self._on_status(f"Connection error: {exc}")
                self._close_from_reader()
                return

            if not chunk:
                self._on_status("Connection closed by CyBot")
                self._close_from_reader()
                return

            buffer += chunk
            while b"\n" in buffer:
                raw_line, buffer = buffer.split(b"\n", 1)
                line = raw_line.decode("ascii", errors="replace").strip("\r")
                if line:
                    self._on_line(line)

    def _close_from_reader(self) -> None:
        self._stop.set()
        sock = self._sock
        self._sock = None
        if sock is not None:
            sock.close()
