# ADHD Task Board

A fullscreen, touch-optimized task management board designed specifically for people with ADHD. It is ideally suited as a standalone, "always-on" application running on a dedicated device like a Raspberry Pi with a touchscreen. It leverages "dopamine hits" from task completion with aggressive visual cues and sound effects, and features a big, clunky, simple design to reduce cognitive load. The system actively nags the user as tasks approach or become overdue to defeat time-blindness.



## Features
- **Big Touch Controls**: Designed for fat fingers on touch screens.
- **Visual Urgency**: Tasks change color and flash as deadlines approach.
- **Voice Monkey Integration**: Spoken alerts via Alexa devices for morning briefings and deadlines.
- **Custom Intervals**: Support for complex recurring tasks (e.g., every 2 days, every 3 weeks).
- **Mobile View**: A simplified list view for ticking off tasks on the go.

## Voice Monkey Integration
Voice Monkey is a service that allows this app to trigger Amazon Alexa devices to speak or play sounds. If you want voice alerts for morning briefings and deadlines:
1. Create a Voice Monkey account and get a token.
2. Define your Alexa devices in `config.json`.

If you do not want to use Voice Monkey, simply leave the `VM_TOKEN`, `VM_DEVICE`, and `VM_MORNING_DEVICE` fields out of `config.json` (or leave them blank), and the app will skip all voice alerts without error.

## Installation

1. Clone the repository.
2. Install dependencies: `pip install -r requirements.txt`
3. Copy `config.json.example` to `config.json` and fill in your Voice Monkey token.
4. Run the app: `python app.py`

## Mobile Access & Remote Access

The app binds to `0.0.0.0:5000`, meaning it is accessible from any device on the same network.

### 1. Local Network (Wi-Fi)
To access the app on your phone while on the same Wi-Fi:
- Find your computer's local IP address (e.g., `192.168.1.50`).
- Open your mobile browser and go to `http://192.168.1.50:5000`.

### 2. Remote Access (Tailscale)
To access the app from anywhere without port forwarding:
- Install **Tailscale** on both your host machine and your phone.
- Use your host machine's Tailscale IP followed by port `5000` (e.g., `http://100.x.y.z:5000`).
- **Troubleshooting**: If Tailscale fails to connect but local IP works, check the following:
  - Ensure Windows Defender Firewall allows incoming connections on TCP Port `5000`.
  - Ensure your browser is not defaulting to `https://`. Explicitly type `http://`.
