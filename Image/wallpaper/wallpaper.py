
import ctypes
import os
import pathlib
import platform
import subprocess
import time
import json
import requests

TODAY_IMAGE_LOCAL_NAME:str = f'{time.strftime("%Y-%m-%d")}.jpg'
TODAY_IMAGE_LOCAL_PATH: pathlib.Path

BING_JSON_PATH:str = 'https://cn.bing.com/HPImageArchive.aspx?format=js&idx=0&n=1&mkt=zh-CN'


def _set_wallpaper_windows(path: pathlib.Path):
    # SPI_SETDESKWALLPAPER = 0x0014, SPIF_UPDATEINIFILE | SPIF_SENDCHANGE = 0x03
    result = ctypes.windll.user32.SystemParametersInfoW(0x0014, 0, str(path), 0x03)
    if not result:
        raise RuntimeError('Failed to set wallpaper, check the image path or permissions')


def _set_wallpaper_linux(path: pathlib.Path):
    de = (os.environ.get('XDG_CURRENT_DESKTOP', '') or
          os.environ.get('DESKTOP_SESSION', '')).lower()

    if any(x in de for x in ('gnome', 'unity', 'budgie')):
        uri = path.as_uri()
        subprocess.run(['gsettings', 'set', 'org.gnome.desktop.background', 'picture-uri', uri], check=True)
        subprocess.run(['gsettings', 'set', 'org.gnome.desktop.background', 'picture-uri-dark', uri], check=True)
    elif any(x in de for x in ('kde', 'plasma')):
        script = (
            "var ds = desktops();"
            "for (var i = 0; i < ds.length; i++) {"
            "  ds[i].wallpaperPlugin = 'org.kde.image';"
            "  ds[i].currentConfigGroup = ['Wallpaper','org.kde.image','General'];"
            f"  ds[i].writeConfig('Image', 'file://{path}');"
            "}"
        )
        subprocess.run(['qdbus', 'org.kde.plasmashell', '/PlasmaShell',
                        'org.kde.PlasmaShell.evaluateScript', script], check=True)
    elif 'xfce' in de:
        subprocess.run(['xfconf-query', '-c', 'xfce4-desktop',
                        '-p', '/backdrop/screen0/monitor0/workspace0/last-image',
                        '-s', str(path)], check=True)
    elif 'mate' in de:
        subprocess.run(['gsettings', 'set', 'org.mate.background',
                        'picture-filename', str(path)], check=True)
    elif 'cinnamon' in de:
        subprocess.run(['gsettings', 'set', 'org.cinnamon.desktop.background',
                        'picture-uri', path.as_uri()], check=True)
    elif any(x in de for x in ('lxde', 'lxqt')):
        subprocess.run(['pcmanfm', '--set-wallpaper', str(path)], check=True)
    else:
        # Fallback: try feh or nitrogen
        for cmd in (['feh', '--bg-scale', str(path)], ['nitrogen', '--set-scaled', str(path)]):
            try:
                subprocess.run(cmd, check=True)
                return
            except FileNotFoundError:
                continue
        raise RuntimeError(f'Unsupported desktop environment: {de or "unknown"}, please install feh or nitrogen')


def setWallpaper(image_path: str):
    """Set the desktop wallpaper (supports Windows and Linux)"""
    path = pathlib.Path(image_path).resolve()
    if not path.exists():
        raise FileNotFoundError(f'Image file not found: {path}')

    system = platform.system()
    if system == 'Windows':
        _set_wallpaper_windows(path)
    elif system == 'Linux':
        _set_wallpaper_linux(path)
    else:
        raise RuntimeError(f'Unsupported operating system: {system}')

    print(f'Wallpaper set to: {path}')

def downloadbingImg(set_as_wallpaper=False):
    global TODAY_IMAGE_LOCAL_NAME,TODAY_IMAGE_LOCAL_PATH,BING_JSON_PATH

    dir_path = pathlib.Path.cwd() / 'data'
    if not dir_path.exists():
        dir_path.mkdir(parents=True)
    TODAY_IMAGE_LOCAL_PATH = dir_path / TODAY_IMAGE_LOCAL_NAME


    print('Fetching JSON...')
    json_rep = requests.get(BING_JSON_PATH)
    print('Parsing JSON...')
    imgPath = json.loads(json_rep.text)["images"][0]["url"]
    imgurl = "http://cn.bing.com" + imgPath
    print('Downloading image...')
    img = requests.get(imgurl)
    print('Writing file...')
    with open(TODAY_IMAGE_LOCAL_PATH, 'wb') as f:
        f.write(img.content)
    print('File saved.')
    print('Download complete.')

    if set_as_wallpaper:
        setWallpaper(str(TODAY_IMAGE_LOCAL_PATH))

if __name__ == '__main__':
    downloadbingImg(set_as_wallpaper=True)