import sys
import time
from colorama import Fore, Style, init
init(autoreset=True)

def typewriter_karaoke(text, speed=0.03):
    """Плавное появление текста"""
    for char in text:
        sys.stdout.write(Fore.CYAN + char + Style.RESET_ALL)
        sys.stdout.flush()
        time.sleep(speed)
    print()

def karaoke_show(lyrics, bpm=100):
    """Построчный вывод с подсветкой под ритм"""
    beat_time = 60 / bpm
    for line in lyrics.split("\n"):
        if line.strip():
            typewriter_karaoke(line, speed=beat_time / 10)
            time.sleep(beat_time)
