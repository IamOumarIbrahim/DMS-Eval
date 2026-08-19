"""
DMS-Eval Auto-Submit Macro (Scroll Wheel / Middle Click Toggle)
==============================================================
A lightweight, zero-dependency global macro for Label Studio / annotation.

Behavior:
  - Trigger: Click the Scroll Wheel (Middle Mouse Button).
  - Toggle ON:  Sends Ctrl+Enter every 2.0 seconds continuously.
  - Toggle OFF: Pauses immediately and goes idle.
  - Works globally across all Windows applications.
  - Audio feedback: High beep (1000 Hz) on toggle ON, Low beep (500 Hz) on toggle OFF.

Exit:
  - Press Ctrl+C in this terminal window.
"""

import sys
import time
import threading
import ctypes
import winsound

# Win32 Virtual-Key Codes
VK_MBUTTON = 0x04   # Middle mouse button
VK_CONTROL = 0x11   # Ctrl key
VK_RETURN  = 0x0D   # Enter key

KEYEVENTF_KEYUP = 0x0002

user32 = ctypes.windll.user32

# Configurable Interval (seconds)
SUBMIT_INTERVAL_SEC = 2.0

# Global state
macro_running = False
exit_requested = False
state_lock = threading.Lock()

def send_ctrl_enter():
    """Simulate atomic Ctrl + Enter keypress via Win32 keybd_event."""
    # Press Ctrl down
    user32.keybd_event(VK_CONTROL, 0, 0, 0)
    # Press Enter down
    user32.keybd_event(VK_RETURN, 0, 0, 0)
    time.sleep(0.04)
    # Release Enter up
    user32.keybd_event(VK_RETURN, 0, KEYEVENTF_KEYUP, 0)
    # Release Ctrl up
    user32.keybd_event(VK_CONTROL, 0, KEYEVENTF_KEYUP, 0)

def play_audio_feedback(is_on):
    """Play brief audio tone asynchronously."""
    try:
        if is_on:
            winsound.Beep(1000, 120)  # High pitch = ON
        else:
            winsound.Beep(500, 150)   # Low pitch = OFF
    except Exception:
        pass

def macro_worker():
    """Background worker loop executing Ctrl+Enter every SUBMIT_INTERVAL_SEC when active."""
    global macro_running, exit_requested
    
    while not exit_requested:
        with state_lock:
            active = macro_running
            
        if active:
            send_ctrl_enter()
            timestamp = time.strftime("%H:%M:%S")
            print(f"  [{timestamp}] -> Sent Ctrl+Enter (Auto-Submit)", flush=True)
            # Sleep in small 50ms slices to allow instantaneous pause when toggled OFF
            slices = int(SUBMIT_INTERVAL_SEC / 0.05)
            for _ in range(slices):
                if not macro_running or exit_requested:
                    break
                time.sleep(0.05)
        else:
            time.sleep(0.05)

def print_banner():
    """Display startup instructions."""
    print("=" * 65, flush=True)
    print("   DMS-Eval Auto-Submit Macro (Scroll Wheel / Middle Click)   ", flush=True)
    print("=" * 65, flush=True)
    print(" * Trigger:     Click the Scroll Wheel (Middle Mouse Button)", flush=True)
    print(f" * Toggle ON:   Sends Ctrl+Enter every {SUBMIT_INTERVAL_SEC}s continuously", flush=True)
    print(" * Toggle OFF:  Pauses immediately (Idle)", flush=True)
    print(" * Scope:       Works GLOBALLY across all applications", flush=True)
    print(" * Exit:        Press Ctrl+C in this terminal to quit", flush=True)
    print("=" * 65, flush=True)
    print("\n[READY] Listening for Scroll Wheel clicks... (Current State: OFF)\n", flush=True)

def main():
    global macro_running, exit_requested
    
    print_banner()
    
    # Start background execution thread
    worker_thread = threading.Thread(target=macro_worker, daemon=True)
    worker_thread.start()
    
    was_pressed = False
    
    try:
        while True:
            # Poll middle mouse button state
            # GetAsyncKeyState MSB (0x8000) indicates if button is currently down
            is_down = bool(user32.GetAsyncKeyState(VK_MBUTTON) & 0x8000)
            
            # Detect rising edge (button press down)
            if is_down and not was_pressed:
                was_pressed = True
                with state_lock:
                    macro_running = not macro_running
                    current_state = macro_running
                
                # Audio feedback in separate thread to avoid UI lag
                threading.Thread(target=play_audio_feedback, args=(current_state,), daemon=True).start()
                
                timestamp = time.strftime("%H:%M:%S")
                if current_state:
                    print(f"\n[{timestamp}] \033[92m>>> [ON] MACRO ACTIVE - Sending Ctrl+Enter every {SUBMIT_INTERVAL_SEC}s\033[0m", flush=True)
                else:
                    print(f"\n[{timestamp}] \033[91m<<< [OFF] MACRO PAUSED - Idle (Press Scroll Wheel to resume)\033[0m\n", flush=True)
                    
            elif not is_down and was_pressed:
                # Button released (debounce)
                was_pressed = False
                
            time.sleep(0.015)  # ~66Hz polling rate, <0.1% CPU usage
            
    except KeyboardInterrupt:
        print("\n\n[EXIT] Exiting macro. Goodbye!", flush=True)
        exit_requested = True
        sys.exit(0)

if __name__ == "__main__":
    main()
