# CyBot Base Station GUI

Python base-station application for the CPRE 288 FinalProject rover.

The GUI connects directly to the CyBot WiFi board using the same raw TCP link
that PuTTY uses:

```text
Host: 192.168.1.1
Port: 288
Mode: raw TCP
```

From the TM4C side this still behaves like UART text communication. The Python
code sends command bytes and receives newline-terminated status or scan lines.

## Run

```powershell
python -m base_station_gui
```

Run the command from the project root:

```powershell
cd U:\CprE288Workspace\FinalProject
python -m base_station_gui
```

## Bring-Up Checklist

1. Program the CyBot with firmware that calls `uart_init()` and handles incoming
   command bytes.
2. Put the CyBot baseboard in WiFi mode and turn the WiFi board on.
3. Connect the PC to the CyBot WiFi network.
4. Start the GUI and connect to `192.168.1.1` on port `288`.
5. Use the raw test box to send a single known command byte first.
6. Watch the event log for returned UART text from the CyBot.

## Current Protocol Assumptions

Outbound commands are single ASCII characters:

```text
w forward
s backward
a turn left
d turn right
g forward-left
h forward-right
j backward-left
k backward-right
v### set speed in mm/s, for example `v100`
x stop
p ping scan
m sweep scan
o iRobot Open Interface sensor status
t 500 ms wheel movement test
q standby / emergency stop
```

Inbound lines are parsed from the current C helpers when possible:

```text
Object 1:  45  32.50  8.25
Ping: 42.18
```

Unknown lines are still displayed in the event log so the GUI can be useful
while the firmware protocol evolves.

## Field View

The test-field canvas plots detections from scan messages and marks the CyBot
pose. Until the firmware sends real odometry or pose updates, the CyBot location
is an operator-side estimate based on movement commands sent from the GUI.

The Raw Test controls can be used without a CyBot by simulating incoming lines,
for example:

```text
Ping: 42.18
Object 1:  90  42.00  8.00
```

Direction controls are hold-to-drive. Press and hold `W`, `A`, `S`, `D`, or the
matching on-screen direction button to keep sending movement commands every
50 ms. Releasing the key or mouse button sends `x` immediately to stop.
Holding `W+A` or `W+D` sends diagonal arc commands. The speed slider sends the
current target speed to the firmware as `v###` after a short debounce so slider
movement does not flood the command stream. After non-drive changes, the GUI
requests `OI:` status and uses distance/angle feedback to update the field view.
