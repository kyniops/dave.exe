# main.py
# Version noir & blanc — multiple fenêtres prank (inoffensif)
# Compatible PyInstaller, musique "musique.mp3" (boucle), son par-fenêtre "musique2.mp3"
import tkinter as tk
import threading
import random
import os
import sys
import ctypes
import subprocess
import winreg
from PIL import Image
from ctypes import POINTER, cast
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume



#################################### Variables changables ################################
volume_windows = 1.0 # 1.0 = 100%

USE_PYGAME = True
MAX_WINDOWS = 50
SPAWN_COUNT = MAX_WINDOWS
SPAWN_INTERVAL_MS = 200

##########################################################################################

# ---- Chemin relatif pour PyInstaller ----
if getattr(sys, 'frozen', False):
    app_path = sys._MEIPASS
else:
    app_path = os.path.dirname(os.path.abspath(__file__))

MUSIC_FILE = os.path.join(app_path, "musique.mp3")     # musique de fond (boucle)
MUSIC2_FILE = os.path.join(app_path, "musique2.mp3")   # son à jouer à chaque fenêtre

# ---- Musique / sons ----
music_player = {"active": False}
_sound2 = None

def _no_audio_play(func_name, exc):
    def f(*a, **k):
        print(f"[{func_name}] impossible de lire le son :", exc, file=sys.stderr)
    return f

try:
    if USE_PYGAME:
        import pygame
        pygame.mixer.init()
        # musique de fond
        if os.path.isfile(MUSIC_FILE):
            try:
                pygame.mixer.music.load(MUSIC_FILE)
            except Exception as e:
                print("Erreur chargement musique de fond:", e, file=sys.stderr)
        # son par-fenêtre
        if os.path.isfile(MUSIC2_FILE):
            try:
                _sound2 = pygame.mixer.Sound(MUSIC2_FILE)
            except Exception as e:
                print("Erreur chargement musique2:", e, file=sys.stderr)

        def play_music():
            try:
                if os.path.isfile(MUSIC_FILE):
                    pygame.mixer.music.play(-1)
                    music_player["active"] = True
            except Exception as e:
                print("Impossible de lire la musique de fond :", e, file=sys.stderr)
                music_player["active"] = False

        def stop_music():
            try:
                pygame.mixer.music.stop()
            except Exception:
                pass
            music_player["active"] = False

        def play_sound_once():
            try:
                if _sound2 is not None:
                    ch = pygame.mixer.find_channel(True)
                    ch.play(_sound2)
                elif os.path.isfile(MUSIC2_FILE):
                    tmp = pygame.mixer.Sound(MUSIC2_FILE)
                    ch = pygame.mixer.find_channel(True)
                    ch.play(tmp)
            except Exception as e:
                print("Impossible de jouer musique2 :", e, file=sys.stderr)
    else:
        import winsound
        def play_music():
            if os.path.isfile(MUSIC_FILE):
                winsound.PlaySound(MUSIC_FILE, winsound.SND_FILENAME | winsound.SND_LOOP | winsound.SND_ASYNC)
                music_player["active"] = True
        def stop_music():
            winsound.PlaySound(None, winsound.SND_PURGE)
            music_player["active"] = False
        def play_sound_once():
            if os.path.isfile(MUSIC2_FILE):
                winsound.PlaySound(MUSIC2_FILE, winsound.SND_FILENAME | winsound.SND_ASYNC)
except Exception as e:
    import sys as _sys
    def play_music():
        print("Impossible de lire la musique de fond :", e, file=_sys.stderr)
        music_player["active"] = False
    def stop_music():
        music_player["active"] = False
    def play_sound_once():
        print("Impossible de jouer musique2 :", e, file=_sys.stderr)

# ---- UI principal (cachée) ----
root = tk.Tk()
root.withdraw()  # on cache la fenêtre principale

open_windows = []
spawning = {"active": False}
# Permettre / bloquer le redémarrage automatique lorsque toutes les fenêtres sont fermées
allow_restart = True
restarting = {"active": False}

# ---- Fonctions ----
def make_prank_window(idx):
    w = tk.Toplevel(root)
    w.title(f"dave.exe")
    w.geometry("360x110")
    w.resizable(False, False)

    sw, sh = w.winfo_screenwidth(), w.winfo_screenheight()
    x = random.randint(0, max(0, sw - 360))
    y = random.randint(0, max(0, sh - 110 - 40))
    w.geometry(f"+{x}+{y}")

    w_state = {"bg_black": True}
    w.configure(bg="#000000")

    msg = tk.Label(w, text="⚠️𓆩×͜×𓆪ALERTE — Système infecté 𓆩×͜×𓆪⚠️", font=("Segoe UI", 14), 
                   bg="#000000", fg="#FFFFFF")
    msg.pack(expand=True, pady=6)

    def close_this():
        w.alive = False
        try:
            open_windows.remove(w)
        except Exception:
            pass
        w.destroy()

    # Assurer que la fermeture via le bouton "X" passe par close_this()
    try:
        w.protocol("WM_DELETE_WINDOW", close_this)
    except Exception:
        pass


    def clignoter():
        if not getattr(w, "alive", True):
            return
        w_state["bg_black"] = not w_state["bg_black"]
        if w_state["bg_black"]:
            bg, fg, bbg, bfg = "#000000", "#FFFFFF", "#FFFFFF", "#000000"
        else:
            bg, fg, bbg, bfg = "#FFFFFF", "#000000", "#000000", "#FFFFFF"
        try:
            w.configure(bg=bg)
            msg.configure(bg=bg, fg=fg)
            # 'btn' n'existe pas toujours; récupérer depuis locals() sans référencer
            _btn = locals().get('btn')
            if _btn is not None:
                try:
                    _btn.configure(bg=bbg, fg=bfg)
                except Exception:
                    pass
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

    try:
        threading.Thread(target=play_sound_once, daemon=True).start()
    except Exception as e:
        print("Erreur lors du play_sound_once:", e, file=sys.stderr)

    return w

def spawn_windows(count=SPAWN_COUNT, interval_ms=SPAWN_INTERVAL_MS):
    if spawning["active"]:
        return
    spawning["active"] = True
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

import os
import sys


def resource_path(relative_path):
    """Retourne le chemin absolu pour PyInstaller"""
    if getattr(sys, 'frozen', False):
        # PyInstaller crée un dossier temporaire _MEIPASS
        base_path = getattr(sys, '_MEIPASS', os.path.dirname(sys.executable))
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)


def changer_fond_decran(image_path):
    ctypes.windll.user32.SystemParametersInfoW(20, 0, image_path, 3)
    abs_path = os.path.abspath(image_path)

    # Convertir en BMP si nécessaire
    if not abs_path.lower().endswith(".bmp"):
        bmp_path = abs_path.rsplit(".", 1)[0] + ".bmp"
        Image.open(abs_path).save(bmp_path, "BMP")
        abs_path = bmp_path

    # Mettre à jour le registre pour rendre le fond d'écran permanent
    key = winreg.OpenKey(
        winreg.HKEY_CURRENT_USER,
        "Control Panel\\Desktop",
        0,
        winreg.KEY_SET_VALUE
    )
    winreg.SetValueEx(key, "Wallpaper", 0, winreg.REG_SZ, abs_path)
    winreg.CloseKey(key)

    # Appliquer immédiatement le fond d'écran
    ctypes.windll.user32.SystemParametersInfoW(20, 0, abs_path, 3)

image_path = resource_path("prank.jpg")  # ou prank.bmp si tu utilises BMP
threading.Thread(target=changer_fond_decran, args=(image_path,), daemon=True).start()

def stop_all():
    # Lorsque l'on ferme volontairement toutes les fenêtres (Escape / on_close),
    # on ne veut pas déclencher le redémarrage automatique.
    global allow_restart
    allow_restart = False
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


def restart_pc(delay_seconds: int = 5):
    """
    Redémarre la machine Windows après un court délai (par défaut 5s).
    Utilise la commande `shutdown`.
    """
    if restarting.get("active"):
        return
    restarting["active"] = True
    try:
        # Stopper la musique proprement
        try:
            stop_music()
        except Exception:
            pass
        # Lancer le shutdown. /r = restart, /t = timeout en secondes
        subprocess.Popen(["shutdown", "/r", "/t", str(delay_seconds)])
    except Exception as e:
        print("Impossible de lancer le redémarrage:", e, file=sys.stderr)


def monitor_windows(interval_ms: int = 1000):
    """Vérifie périodiquement la liste open_windows et déclenche restart_pc()
    lorsque toutes les fenêtres ont été fermées par l'utilisateur (et que
    stop_all() n'a pas demandé d'empêcher le reboot).
    """
    try:
        # Si le redémarrage a été explicitement bloqué ou déjà démarré, rien à faire
        if not allow_restart or restarting.get("active"):
            return
        # Si aucune fenêtre d'alerte n'est ouverte et qu'on n'est pas en train
        # de spawner, on redémarre
        if len(open_windows) == 0 and not spawning.get("active"):
            # Petit délai avant reboot (utilise 5s par défaut)
            restart_pc(delay_seconds=5)
            return
    finally:
        # Replanifier la surveillance si l'application est toujours active
        try:
            if root.winfo_exists() and not restarting.get("active"):
                root.after(interval_ms, monitor_windows)
        except Exception:
            pass

def on_close():
    stop_all()
    root.destroy()

def changer_son(x: float):
    """
    Change le volume système Windows et enlève le mute si nécessaire.
    :param x: valeur entre 0.0 (0%) et 1.0 (100%)
    """
    devices = AudioUtilities.GetSpeakers()
    interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
    volume = cast(interface, POINTER(IAudioEndpointVolume))

    # Enlever le mute si activé
    if volume.GetMute():
        volume.SetMute(0, None)

    # Régler le volume
    volume.SetMasterVolumeLevelScalar(min(max(x, 0.0), 1.0), None)

root.protocol("WM_DELETE_WINDOW", on_close)
root.bind("<Escape>", lambda e: stop_all())
changer_son(volume_windows) #Change le son de windows
image_path = resource_path("prank.jpg")  # ou prank.bmp si tu utilises BMP
threading.Thread(target=changer_fond_decran, args=(image_path,), daemon=True).start()

# --- Lancer directement les fenêtres au démarrage ---
spawn_windows()

# Démarrer le monitor qui lancera le redémarrage si toutes les fenêtres sont fermées
try:
    root.after(1000, monitor_windows)
except Exception:
    pass

root.mainloop()
