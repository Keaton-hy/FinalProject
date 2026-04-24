from __future__ import annotations

from dataclasses import dataclass
import re


DEFAULT_HOST = "192.168.1.1"
DEFAULT_PORT = 288


COMMANDS = {
    "forward": "w",
    "backward": "s",
    "left": "a",
    "right": "d",
    "forward_left": "g",
    "forward_right": "h",
    "backward_left": "j",
    "backward_right": "k",
    "stop": "x",
    "ping": "p",
    "sweep": "m",
    "oi_status": "o",
    "wheel_test": "t",
    "standby": "q",
}


@dataclass(frozen=True)
class PingReading:
    distance_cm: float


@dataclass(frozen=True)
class ObjectReading:
    object_num: int
    angle_deg: int
    distance_cm: float
    radial_width: float


@dataclass(frozen=True)
class RawLine:
    text: str


@dataclass(frozen=True)
class OIStatus:
    bump_left: bool
    bump_right: bool
    cliff_left: bool
    cliff_front_left: bool
    cliff_front_right: bool
    cliff_right: bool
    distance_mm: float
    angle_deg: float


ParsedLine = PingReading | ObjectReading | OIStatus | RawLine

_PING_RE = re.compile(r"^Ping:\s*(?P<distance>-?\d+(?:\.\d+)?)\s*$", re.IGNORECASE)
_OBJECT_RE = re.compile(
    r"^Object\s+(?P<num>\d+):\s+"
    r"(?P<angle>-?\d+)\s+"
    r"(?P<distance>-?\d+(?:\.\d+)?)\s+"
    r"(?P<width>-?\d+(?:\.\d+)?)\s*$",
    re.IGNORECASE,
)
_OI_RE = re.compile(
    r"^OI:\s+"
    r"bumpL=(?P<bump_l>[01])\s+"
    r"bumpR=(?P<bump_r>[01])\s+"
    r"cliffL=(?P<cliff_l>[01])\s+"
    r"cliffFL=(?P<cliff_fl>[01])\s+"
    r"cliffFR=(?P<cliff_fr>[01])\s+"
    r"cliffR=(?P<cliff_r>[01])\s+"
    r"dist=(?P<distance>-?\d+(?:\.\d+)?)\s+"
    r"angle=(?P<angle>-?\d+(?:\.\d+)?)\s*$",
    re.IGNORECASE,
)


def encode_command(command: str) -> bytes:
    if command.startswith("v") and command[1:].isdigit():
        return f"{command}\n".encode("ascii")
    if len(command) == 1:
        return command.encode("ascii")
    if command not in COMMANDS:
        raise ValueError(f"Unknown command: {command}")
    return COMMANDS[command].encode("ascii")


def parse_line(line: str) -> ParsedLine:
    text = line.strip()

    ping_match = _PING_RE.match(text)
    if ping_match:
        return PingReading(distance_cm=float(ping_match.group("distance")))

    object_match = _OBJECT_RE.match(text)
    if object_match:
        return ObjectReading(
            object_num=int(object_match.group("num")),
            angle_deg=int(object_match.group("angle")),
            distance_cm=float(object_match.group("distance")),
            radial_width=float(object_match.group("width")),
        )

    oi_match = _OI_RE.match(text)
    if oi_match:
        return OIStatus(
            bump_left=oi_match.group("bump_l") == "1",
            bump_right=oi_match.group("bump_r") == "1",
            cliff_left=oi_match.group("cliff_l") == "1",
            cliff_front_left=oi_match.group("cliff_fl") == "1",
            cliff_front_right=oi_match.group("cliff_fr") == "1",
            cliff_right=oi_match.group("cliff_r") == "1",
            distance_mm=float(oi_match.group("distance")),
            angle_deg=float(oi_match.group("angle")),
        )

    return RawLine(text=text)
