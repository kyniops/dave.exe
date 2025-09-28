# main.py
# Version noir & blanc — multiple fenêtres prank (inoffensif)
# Lance directement sans UI principale
# Compatible PyInstaller, musique "musique.mp3"

import tkinter as tk
import threading
import random
import os
import sys

USE_PYGAME = True
MAX_WINDOWS = 50
SPAWN_COUNT = MAX_WINDOWS
SPAWN_INTERVAL_MS = 200

# ---- Chemin relatif pour PyInstaller ----
if getattr(sys, 'frozen', False):
    app_path = sys._MEIPASS
else:
    app_path = os.path.dirname(os.path.abspath(__file__))

MUSIC_FILE = os.path.join(app_path, "musique.mp3")

# ---- Musique ----
music_player = {"active": False}
try:
    if USE_PYGAME:
        import pygame
        pygame.mixer.init()
        if not os.path.isfile(MUSIC_FILE):
            raise FileNotFoundError(f"{MUSIC_FILE} introuvable.")
        pygame.mixer.music.load(MUSIC_FILE)
        def play_music():
            pygame.mixer.music.play(-1)
            music_player["active"] = True
        def stop_music():
            try:
                pygame.mixer.music.stop()
            except Exception:
                pass
            music_player["active"] = False
    else:
        import winsound
        def play_music():
            if os.path.isfile(MUSIC_FILE):
                winsound.PlaySound(MUSIC_FILE, winsound.SND_FILENAME | winsound.SND_LOOP | winsound.SND_ASYNC)
                music_player["active"] = True
        def stop_music():
            winsound.PlaySound(None, winsound.SND_PURGE)
            music_player["active"] = False
except Exception as e:
    def play_music():
        print("Impossible de lire la musique :", e, file=sys.stderr)
        music_player["active"] = False
    def stop_music():
        music_player["active"] = False

# ---- Initialisation tkinter (fenêtre principale cachée) ----
root = tk.Tk()
root.title("dave.exe")
root.geometry("1x1+0+0")  # petite fenêtre invisible
root.overrideredirect(True)  # pas de bordures
root.withdraw()  # cache la fenêtre principale

BW_BG = "#000000"
BW_FG = "#FFFFFF"
BW_BTN_BG = "#FFFFFF"
BW_BTN_FG = "#000000"

open_windows = []
spawning = {"active": False}

# ---- Fonctions ----
def make_prank_window(idx):
    w = tk.Toplevel(root)
    w.title("dave.exe")
    w.geometry("360x110")
    w.resizable(False, False)

    sw, sh = w.winfo_screenwidth(), w.winfo_screenheight()
    x = random.randint(0, max(0, sw - 360))
    y = random.randint(0, max(0, sh - 110 - 40))
    w.geometry(f"+{x}+{y}")

    w_state = {"bg_black": True}
    w.configure(bg=BW_BG)

    msg = tk.Label(w, text="⚠️𓆩×͜×𓆪ALERTE — Système infecté 𓆩×͜×𓆪⚠️", font=("Segoe UI", 14), bg=BW_BG, fg=BW_FG)
    msg.pack(expand=True, pady=6)

    def close_this():
        w.alive = False
        try:
            open_windows.remove(w)
        except Exception:
            pass
        try:
            w.destroy()
        except Exception:
            pass

    btn = tk.Button(w, text="Fermer", command=close_this, bg=BW_BTN_BG, fg=BW_BTN_FG)
    btn.pack(side="bottom", pady=(0,6))

    def clignoter():
        if not getattr(w, "alive", True):
            return
        w_state["bg_black"] = not w_state["bg_black"]
        if w_state["bg_black"]:
            bg, fg, bbg, bfg = BW_BG, BW_FG, BW_BTN_BG, BW_BTN_FG
        else:
            bg, fg, bbg, bfg = BW_FG, BW_BG, BW_BG, BW_FG
        try:
            w.configure(bg=bg)
            msg.configure(bg=bg, fg=fg)
            btn.configure(bg=bbg, fg=bfg)
        except Exception:
            pass
        w.after(450, clignoter)

    def wiggle():
        if not getattr(w, "alive", True):
            return
        dx = random.randint(-6, 6)
        dy = random.randint(-5, 5)
        try:
            geom = w.geometry().split("+")
            base = geom[1:]
            newx = max(0, int(base[0]) + dx)
            newy = max(0, int(base[1]) + dy)
            w.geometry(f"+{newx}+{newy}")
        except Exception:
            pass
        w.after(random.randint(400, 1000), wiggle)

    w.alive = True
    clignoter()
    wiggle()
    return w

def spawn_windows(count=SPAWN_COUNT, interval_ms=SPAWN_INTERVAL_MS):
    if spawning["active"]:
        return
    spawning["active"] = True
    # musique en thread pour ne pas bloquer la boucle Tk
    threading.Thread(target=play_music, daemon=True).start()
    created = 0
    def _spawn_step():
        nonlocal created
        if created >= count or len(open_windows) >= MAX_WINDOWS or not spawning["active"]:
            spawning["active"] = False
            return
        w = make_prank_window(created)
        open_windows.append(w)
        created += 1
        root.after(interval_ms, _spawn_step)
    _spawn_step()

def stop_all(event=None):
    spawning["active"] = False
    try:
        stop_music()
    except Exception:
        pass
    for w in open_windows[:]:
        try:
            w.alive = False
            w.destroy()
        except Exception:
            pass
    open_windows.clear()
    try:
        root.quit()
    except Exception:
        pass

# Bind global Escape pour arrêter (utile car fenêtre principale est cachée)
root.bind_all("<Escape>", stop_all)

# Lance automatiquement après le démarrage de la boucle Tk
root.after(50, spawn_windows)

# Assure une fermeture propre si le processus reçoit kill via la fenêtre principale
def on_close():
    stop_all()
    try:
        root.destroy()
    except Exception:
        pass

root.protocol("WM_DELETE_WINDOW", on_close)

# Démarre la boucle événements Tk (la fenêtre principale reste cachée)
root.mainloop()
