# ADHD Task Board

Welcome to the **ADHD Task Board**! This app is a purpose-built physiological and cognitive externalisation of your executive function. It is designed specifically to help neurodivergent minds bypass the "wall of awful" associated with digital planners. 

By utilizing a high-contrast, stripped-back interface, this app combats time blindness through a visual progress bar system that converts abstract deadlines into tangible, shrinking geometric areas. It prioritizes a "top-five" hierarchy to prevent choice paralysis, ensuring that only your most critical objectives occupy your primary visual field. Secondary tasks are relegated to a sub-queue to minimize cognitive load.

The system requires zero maintenance once an initial schedule is established. To accommodate the ADHD brain's need for novelty and immediate dopamine, the app utilizes celebratory UI finales and auditory rewards to provide the high-energy feedback necessary for task completion.

---

## 🛠️ 1. Installation

This app is run using Python. Don't worry if you're not a programmer, the steps are straightforward! 

### Windows Instructions:
1. Open your Command Prompt (`cmd`) or PowerShell.
2. Navigate to the folder where you want to install it. For example, if you want it on your C drive:
   ```cmd
   cd C:\
   ```
3. Clone the repository and go inside the new folder:
   ```cmd
   git clone https://github.com/TheSharmanator/adhdtaskmanager.git
   cd adhdtaskmanager
   ```
4. Install the required Python packages:
   ```cmd
   pip install -r requirements.txt
   ```
5. **CRITICAL STEP:** You must set up your configuration file before running the app.
   - Look for the file named `config.json.example`.
   - Rename it to just `config.json` (remove the `.example` part).
   - Open `config.json` in a text editor (like Notepad) and fill in your details (see Voice Monkey section below).
6. Run the app! Make sure you are inside the `adhdtaskmanager` folder, then type:
   ```cmd
   python app.py
   ```

### Linux / Raspberry Pi Instructions:
1. Open your Terminal.
2. Navigate to your user directory:
   ```bash
   cd /home/user/
   ```
3. Clone the repository and enter the directory:
   ```bash
   git clone https://github.com/TheSharmanator/adhdtaskmanager.git
   cd adhdtaskmanager
   ```
4. Install the required packages:
   ```bash
   pip3 install -r requirements.txt
   ```
5. **CRITICAL STEP:** Prepare your config file.
   ```bash
   mv config.json.example config.json
   nano config.json
   ```
   Fill in your details and save (`Ctrl+X`, `Y`, `Enter`).
6. Run the app:
   ```bash
   python3 app.py
   ```

---

## 🐒 2. Voice Monkey Integration

Voice Monkey allows the app to give you auditory feedback, praises, and nags through your Alexa devices. This breaks hyperfocus and gives you a dopamine hit when you complete a task.

1. Go to the Voice Monkey website: [https://voicemonkey.io/](https://voicemonkey.io/)
2. Log in using your **Amazon Account**.
3. Open the **Alexa App** on your phone and add the **Voice Monkey Skill**.
4. Go back to the Voice Monkey dashboard in your browser and click on **Manage Devices**.
5. Press **Add Speaker**.
6. Give the device a name (e.g., "ADHD Board"). *Note: This is just a virtual name, not a physical Alexa device.*
7. Press **Next**.
8. Go to **Devices** in your Alexa App. You should see the new device you just made. Click on it and **Toggle OFF** "Doorbell Press Notifications".
9. Go to **Routines** in the Alexa App and press the **+** button.
10. Click **Add an Event**, select **Smart Home**, then select the device you just added from Voice Monkey. Hit **Save**.
11. Press **Add an Action**. Select **Skills**, then **Your Skills**, then **Voice Monkey**, then **Next**.
12. Press **Save**. Alexa will ask which device you want it to respond from. Choose your physical Alexa speaker.
13. Go back to the Voice Monkey console and click **Sync Device**. You will hear a test announcement!
14. Finally, go to **API Credentials** in the Voice Monkey console and copy the **token**.
15. Open your `config.json` file. Set `"VM": true`. Paste your token into the token field. Set `"VM Device alerts and briefings"` to the exact name of the device you created in step 6. Put your name in the User Name field.

---

## 🌐 3. Tailscale Setup (Remote Access)

Why install Tailscale? 
There is a "simple" remote version of this app designed for adding or completing tasks while you are away from the main board. Tailscale creates a secure, private network between your devices, allowing your phone or laptop to talk to your Task Board from anywhere in the world, securely, without opening router ports.

1. Go to [https://tailscale.com/](https://tailscale.com/) and create a free account.
2. Install Tailscale on the device running the Task Board (e.g., your Raspberry Pi or PC).
3. Log in to Tailscale on that device.
4. Install Tailscale on your mobile phone or laptop. Log into the same account.
5. Once both devices are connected, open the Tailscale app. You will see an IP address for your Task Board device (it usually starts with `100.x.x.x`).
6. On your phone, open your browser and type that IP address followed by `:5001` (e.g., `http://100.x.x.x:5001`). 
7. You now have remote access to your tasks!

---

## 🖥️ 4. What is Kiosk Mode?

This app is optimally designed for **Always-On Devices in Kiosk Mode**. 

**Kiosk Mode** forces a web browser to run in absolute full-screen. There are no address bars, no tabs, no close buttons, and no distractions. It turns a regular monitor or tablet into a dedicated, single-purpose appliance.

Because the app is meant to be a constant visual anchor in your room, it is highly suited for minimal, low-power setups like a **Raspberry Pi** plugged into a spare monitor.

---

## 🚀 5. Running in Kiosk Mode

Follow these steps to launch the app as a dedicated kiosk:

### Step A: Find your Browser and IP
1. **Find your browser command (Linux):** 
   Open a terminal and type:
   ```bash
   which chromium-browser chromium
   ```
   Note the output (e.g., `/usr/bin/chromium-browser`). If you are on Windows, your browser is likely `msedge.exe` or `chrome.exe`.

2. **Get your IP Address:**
   - **Linux:** Type `hostname -I` in the terminal.
   - **Windows:** Type `ipconfig` in Command Prompt and look for "IPv4 Address".

### Step B: The Kiosk Command
Using the information from above, run this command in your terminal/command prompt (replace the bracketed info with your actual details):
```bash
{browsername} --kiosk --noerrdialogs --disable-infobars http://{ip address}:5001
```

### Step C: Creating a Desktop Shortcut
**On Windows:**
1. Right-click your Desktop > **New** > **Shortcut**.
2. For the location, type the path to your browser followed by the kiosk arguments. Example:
   ```cmd
   "C:\Program Files\Google\Chrome\Application\chrome.exe" --kiosk --noerrdialogs --disable-infobars http://localhost:5001
   ```
3. Name it "Task Board Kiosk" and click Finish.

**On Linux (Raspberry Pi):**
1. Right-click your desktop and select **Create New** > **Shortcut** (or create a `.desktop` file).
2. For the command, use:
   ```bash
   chromium-browser --kiosk --noerrdialogs --disable-infobars http://localhost:5001
   ```

### Step D: Autoboot Instructions (Advanced)
To make your device truly feel like an appliance, it should boot straight into the app.

**Linux (Raspberry Pi via Autostart):**
1. Open terminal and edit the autostart file:
   ```bash
   nano ~/.config/lxsession/LXDE-pi/autostart
   ```
2. Add these two lines at the bottom. The first starts the server, the second starts the browser. *(Make sure the path matches where you cloned the repo)*:
   ```bash
   @bash -c "cd /home/pi/adhdtaskmanager && python3 app.py"
   @chromium-browser --kiosk --noerrdialogs --disable-infobars http://localhost:5001
   ```

**Windows:**
1. Press `Win + R`, type `shell:startup`, and hit Enter.
2. Create a batch file (`start_board.bat`) in this folder.
3. Edit the file in Notepad and add:
   ```cmd
   @echo off
   cd C:\adhdtaskmanager
   start /B python app.py
   timeout /t 5
   start "C:\Program Files\Google\Chrome\Application\chrome.exe" --kiosk --noerrdialogs --disable-infobars http://localhost:5001
   ```
4. Save it. Every time Windows boots, your board will launch automatically!
