## README — dave.exe
- Note importante : utilise ce programme uniquement sur ta machine ou avec l’accord explicite de la personne ciblée. Ne cause pas de panique ni de perte de travail non sauvegardé — reste responsable. ⚠️

## Résumé rapide :
- dave.exe est un petit prank visuel : il ouvre des fenêtres Toplevel noires/blanches qui clignotent et bougent, joue éventuellement une boucle audio, et laisse un bouton Fermer sur chaque fenêtre. De plus, le programme change le fond d'écran du pc. Le son est mis à fond. Le script est pensé pour être empaqueté en .exe avec PyInstaller et personnalisable en quelques variables.

## Télécharge : 
ici: [Télécharger](https://www.mediafire.com/file/5h1jfq2mkyry95s/dave_land.exe/file)

## Requirements

Ce projet nécessite Python 3.x et les packages suivants :

### Installation des dépendances

Vous pouvez installer toutes les dépendances avec `pip` :

```bash
pip install pillow comtypes pycaw
```
## PY TO EXE

```bash
pyinstaller --onefile --noconsole --add-data "musique.mp3;." --add-data "musique2.mp3;." --add-data "prank.jpg;." --icon=icone.ico main.py
```
ou
```bash
py -m pip install --user pyinstaller; py -m PyInstaller --onefile --noconsole --add-data "musique.mp3;." --add-data "musique2.MP3;." --add-data "prank.jpg;." --icon=icone.ico main.py


