import evdev
from evdev import ecodes, InputDevice
import threading
import time
import select

class HotkeyListener:
    def __init__(self, hotkey_str, callback):
        self.hotkey_str = hotkey_str
        self.callback = callback
        self.running = False
        self.thread = None
        self.pressed_keys = set()
        
        # Parse hotkey string (e.g., "Ctrl+Shift+S")
        self.target_keys = self.parse_hotkey(hotkey_str)
        print(f"Target keys parsed: {self.target_keys}")

    def parse_hotkey(self, hotkey_str):
        # Map common names to evdev constants
        mapping = {
            'ctrl': [ecodes.KEY_LEFTCTRL, ecodes.KEY_RIGHTCTRL],
            'shift': [ecodes.KEY_LEFTSHIFT, ecodes.KEY_RIGHTSHIFT],
            'alt': [ecodes.KEY_LEFTALT, ecodes.KEY_RIGHTALT],
            'meta': [ecodes.KEY_LEFTMETA, ecodes.KEY_RIGHTMETA],
            'super': [ecodes.KEY_LEFTMETA, ecodes.KEY_RIGHTMETA],
            'win': [ecodes.KEY_LEFTMETA, ecodes.KEY_RIGHTMETA],
            'cmd': [ecodes.KEY_LEFTMETA, ecodes.KEY_RIGHTMETA],
            'enter': [ecodes.KEY_ENTER],
            'esc': [ecodes.KEY_ESC],
            'tab': [ecodes.KEY_TAB],
            'space': [ecodes.KEY_SPACE],
            'backspace': [ecodes.KEY_BACKSPACE],
            '`': [ecodes.KEY_GRAVE],
            '~': [ecodes.KEY_GRAVE],
            '-': [ecodes.KEY_MINUS],
            '_': [ecodes.KEY_MINUS],
            '=': [ecodes.KEY_EQUAL],
            '+': [ecodes.KEY_EQUAL], # Shift+= is + but the key is equal
            '[': [ecodes.KEY_LEFTBRACE],
            '{': [ecodes.KEY_LEFTBRACE],
            ']': [ecodes.KEY_RIGHTBRACE],
            '}': [ecodes.KEY_RIGHTBRACE],
            '\\': [ecodes.KEY_BACKSLASH],
            '|': [ecodes.KEY_BACKSLASH],
            ';': [ecodes.KEY_SEMICOLON],
            ':': [ecodes.KEY_SEMICOLON],
            '\'': [ecodes.KEY_APOSTROPHE],
            '"': [ecodes.KEY_APOSTROPHE],
            ',': [ecodes.KEY_COMMA],
            '<': [ecodes.KEY_COMMA],
            '.': [ecodes.KEY_DOT],
            '>': [ecodes.KEY_DOT],
            '/': [ecodes.KEY_SLASH],
            '?': [ecodes.KEY_SLASH],
        }
        
        parts = hotkey_str.lower().split('+')
        target_set = []
        
        for p in parts:
            p = p.strip()
            if p in mapping:
                target_set.append(set(mapping[p]))
            else:
                # Try to find key by name
                key_name = f"KEY_{p.upper()}"
                if hasattr(ecodes, key_name):
                    target_set.append({getattr(ecodes, key_name)})
                else:
                    print(f"Warning: Unknown key '{p}'")
        
        return target_set

    def find_keyboards(self):
        devices = [InputDevice(path) for path in evdev.list_devices()]
        keyboards = []
        for dev in devices:
            # Check if device has keys
            cap = dev.capabilities()
            if ecodes.EV_KEY in cap:
                # Check for specific keys to verify it's a keyboard (e.g., KEY_A, KEY_ENTER)
                keys = cap[ecodes.EV_KEY]
                if ecodes.KEY_A in keys or ecodes.KEY_ENTER in keys:
                     keyboards.append(dev)
        return keyboards

    def start(self):
        if self.running: return
        self.running = True
        self.thread = threading.Thread(target=self.loop, daemon=True)
        self.thread.start()

    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join(timeout=1.0)

    def loop(self):
        keyboards = self.find_keyboards()
        if not keyboards:
            print("No keyboards found for hotkey listening.")
            return

        print(f"Listening on {len(keyboards)} keyboards: {[k.name for k in keyboards]}")
        
        # Prepare for select
        fds = {dev.fd: dev for dev in keyboards}
        
        while self.running:
            r, w, x = select.select(fds, [], [], 1.0)
            for fd in r:
                dev = fds[fd]
                try:
                    for event in dev.read():
                        if event.type == ecodes.EV_KEY:
                            self.handle_key_event(event)
                except OSError:
                    # Device might be disconnected
                    pass

    def handle_key_event(self, event):
        if event.value == 1: # Key pressed
            self.pressed_keys.add(event.code)
            self.check_hotkey()
        elif event.value == 0: # Key released
            if event.code in self.pressed_keys:
                self.pressed_keys.remove(event.code)

    def check_hotkey(self):
        # target_keys is a list of sets (possible codes for each position)
        
        match = True
        for required_set in self.target_keys:
            if not required_set.intersection(self.pressed_keys):
                match = False
                break
        
        if match:
             self.callback()

if __name__ == "__main__":
    # Test
    def cb(): print("HOTKEY TRIGGERED!")
    listener = HotkeyListener("ctrl+shift+s", cb)
    listener.start()
    try:
        while True: time.sleep(1)
    except KeyboardInterrupt:
        listener.stop()
