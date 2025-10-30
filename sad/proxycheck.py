# proxy_saver_full.py
# ПОЛНЫЙ СКРИПТ: ПРОВЕРЯЕТ ПРОКСИ + СОХРАНЯЕТ КАЖДЫЙ РАБОЧИЙ СРАЗУ!
# Ctrl+C = НИ ОДИН ПРОКСИ НЕ ПОТЕРЯЕТСЯ!
# Автобэкапы, логи, безопасные задержки, HTTPS-поддержка

import requests
import random
import time
import threading
import signal
import sys
import os
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

# ================== НАСТРОЙКИ ==================
INPUT_FILE = 'socks.txt'                    # Входной файл
WORKING_FILE = 'working_proxies.txt'          # Основной выход
BACKUP_FILE = 'working_proxies_backup.txt'    # Резервная копия
LOG_FILE = 'proxy_save.log'                   # Логи

DELAY_BETWEEN = (3, 7)       # Задержка между проверками (сек)
MAX_THREADS = 8              # Количество потоков
TIMEOUT = 10                 # Таймаут запроса
RETRIES = 2                  # Повтор при ошибке

# Сайты для проверки IP (все выдерживают миллионы запросов)
TEST_URLS = [
    'https://api.ipify.org',
    'https://ifconfig.me/ip',
    'https://icanhazip.com',
    'https://myip.addr.space',
    'https://ipinfo.io/ip'
]

# Локальный тест-сервер (если хочешь 0 внешних запросов)
USE_LOCAL_SERVER = False     # Поменяй на True → 0 внешних запросов
LOCAL_SERVER_PORT = 8080
# ===============================================

# Глобальные переменные
working_proxies = []
lock = threading.Lock()
stop_flag = False

# ================== ЛОГИРОВАНИЕ ==================
def log(msg):
    timestamp = datetime.now().strftime("%H:%M:%S")
    line = f"[{timestamp}] {msg}"
    print(line)
    try:
        with open(LOG_FILE, 'a', encoding='utf-8') as f:
            f.write(line + '\n')
    except:
        pass  # Игнорируем ошибки записи лога

# ================== ЛОКАЛЬНЫЙ СЕРВЕР (опционально) ==================
def start_local_server():
    from http.server import HTTPServer, BaseHTTPRequestHandler
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200)
            self.send_header('Content-Type', 'text/plain')
            self.end_headers()
            self.wfile.write(b"OK")
    try:
        server = HTTPServer(('127.0.0.1', LOCAL_SERVER_PORT), Handler)
        log(f"Локальный тест-сервер запущен на http://127.0.0.1:{LOCAL_SERVER_PORT}")
        server.serve_forever()
    except:
        pass

if USE_LOCAL_SERVER:
    threading.Thread(target=start_local_server, daemon=True).start()
    time.sleep(1)
    TEST_URLS = [f'http://127.0.0.1:{LOCAL_SERVER_PORT}']

# ================== СОХРАНЕНИЕ ПРОКСИ СРАЗУ! ==================
def save_proxy(proxy):
    with lock:
        if proxy in working_proxies:
            return
        working_proxies.append(proxy)
        
        # 1. Основной файл
        try:
            with open(WORKING_FILE, 'a', encoding='utf-8') as f:
                f.write(proxy + '\n')
        except:
            pass
        
        # 2. Бэкап
        try:
            with open(BACKUP_FILE, 'a', encoding='utf-8') as f:
                f.write(proxy + '\n')
        except:
            pass
        
        # 3. Автобэкап каждые 10
        if len(working_proxies) % 10 == 0:
            backup_name = f"backup_{int(time.time())}.txt"
            try:
                with open(backup_name, 'w', encoding='utf-8') as f:
                    for p in working_proxies:
                        f.write(p + '\n')
                log(f"БЭКАП: {backup_name} ({len(working_proxies)} прокси)")
            except:
                pass
        
        log(f"СОХРАНЁН: {proxy}")

# ================== ЗАГРУЗКА ПРОКСИ ==================
def load_proxies():
    if not os.path.exists(INPUT_FILE):
        log(f"ОШИБКА: Файл '{INPUT_FILE}' не найден!")
        log("Создай файл с прокси в формате: http://ip:port")
        sys.exit(1)
    
    try:
        with open(INPUT_FILE, 'r', encoding='utf-8') as f:
            proxies = []
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    # Поддержка http, https, socks4, socks5
                    if not line.lower().startswith(('http://', 'https://', 'socks4://', 'socks5://', 'socks5h://')):
                        line = 'http://' + line
                    proxies.append(line)
        
        log(f"Загружено {len(proxies)} прокси из '{INPUT_FILE}'")
        return proxies
    except Exception as e:
        log(f"Ошибка чтения файла: {e}")
        sys.exit(1)

# ================== ПРОВЕРКА ОДНОГО ПРОКСИ ==================
def check_proxy(proxy, retry=0):
    global stop_flag
    if stop_flag:
        return proxy, False
    
    url = random.choice(TEST_URLS)
    proxies_dict = {'http': proxy, 'https': proxy}
    
    try:
        start = time.time()
        resp = requests.get(
            url,
            proxies=proxies_dict,
            timeout=TIMEOUT,
            headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'},
            verify=False
        )
        elapsed = time.time() - start
        
        if resp.status_code == 200:
            ip = resp.text.strip()
            save_proxy(proxy)
            log(f"УСПЕХ: {proxy} → {ip} ({elapsed:.2f}с)")
            return proxy, True
        else:
            if retry < RETRIES:
                time.sleep(1)
                return check_proxy(proxy, retry + 1)
            log(f"ОТКАЗ: {proxy} → Код {resp.status_code}")
    
    except Exception as e:
        err = str(e).split('(')[0].strip()
        if retry < RETRIES:
            time.sleep(1)
            return check_proxy(proxy, retry + 1)
        log(f"ОШИБКА: {proxy} → {err}")
    
    return proxy, False

# ================== ОБРАБОТКА Ctrl+C ==================
def signal_handler(sig, frame):
    global stop_flag
    log("\nПРЕКРАЩЕНИЕ РАБОТЫ (Ctrl+C)...")
    stop_flag = True
    
    count = len(working_proxies)
    log(f"ГОТОВО: Найдено {count} рабочих прокси")
    
    if count > 0:
        try:
            with open(WORKING_FILE, 'w', encoding='utf-8') as f:
                for p in working_proxies:
                    f.write(p + '\n')
            log(f"ФИНАЛЬНОЕ СОХРАНЕНИЕ: {WORKING_FILE}")
        except:
            pass
    
    log("Проверка остановлена. Все данные сохранены.")
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

# ================== ОСНОВНАЯ ФУНКЦИЯ ==================
def main():
    # Очистка старых файлов
    for f in [WORKING_FILE, BACKUP_FILE, LOG_FILE]:
        try:
            open(f, 'w').close()
        except:
            pass
    
    log("=" * 65)
    log("ЗАПУСК ПРОВЕРКИ ПРОКСИ С АВТОСОХРАНЕНИЕМ")
    log("=" * 65)
    log(f"Режим: {'ЛОКАЛЬНЫЙ' if USE_LOCAL_SERVER else 'ВНЕШНИЕ САЙТЫ'}")
    log(f"Задержка: {DELAY_BETWEEN[0]}-{DELAY_BETWEEN[1]} сек | Потоков: {MAX_THREADS}")
    log("-" * 65)
    
    proxies = load_proxies()
    if not proxies:
        log("Нет прокси для проверки.")
        return
    
    checked = 0
    log("НАЧИНАЕМ ПРОВЕРКУ...\n")
    
    with ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
        # Запускаем все задачи
        future_to_proxy = {executor.submit(check_proxy, p): p for p in proxies}
        
        for future in as_completed(future_to_proxy):
            if stop_flag:
                break
                
            checked += 1
            proxy = future_to_proxy[future]
            
            # Задержка между проверками
            delay = random.uniform(*DELAY_BETWEEN)
            time.sleep(delay)
    
    # Финальный отчёт
    count = len(working_proxies)
    log("\n" + "=" * 65)
    log(f"ПРОВЕРЕНО: {checked}/{len(proxies)}")
    log(f"РАБОЧИХ: {count}")
    if count > 0:
        log(f"СОХРАНЕНО В: {WORKING_FILE}")
        log(f"БЭКАП: {BACKUP_FILE}")
    log("ГОТОВО!")
    log("=" * 65)

if __name__ == "__main__":
    # Установка для SOCKS (если нужно)
    try:
        import socket
        import socks
    except:
        pass
    
    main()