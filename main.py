import os
import time
import smtplib
import random
import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from tqdm import tqdm

# === НАСТРОЙКИ ===
RECIPIENTS = ["abuse@telegram.org", "dmca@telegram.org"]
CHANNEL_LINK = "https://t.me/nikulichko"  # ← ЗАМЕНИ НА НУЖНЫЙ
POST_LINKS = [
    "https://t.me/nikulichko/11",
    "https://t.me/nikulichko/13",
    "https://t.me/nikulichko/4"
]  # ← добавь ссылки на посты с жестокостью

# === ШАБЛОНЫ ЖАЛОБ (уникальные формулировки) ===
TEMPLATES = [
    "Urgent: Animal cruelty content in channel {channel}. Posts: {links}. Videos show animals being beaten and tortured. This violates ToS. Please remove immediately.",
    "I am reporting {channel} for publishing graphic animal abuse. Examples: {links}. Dogs and cats are shown in pain. This is illegal and inhumane. Action required.",
    "Channel {channel} spreads videos of animal torture. See: {links}. This content traumatizes viewers and promotes violence. Please ban the channel.",
    "Please investigate {channel} — they post real videos of animal suffering: {links}. This must be stopped. Thank you for protecting animals.",
    "Animal abuse alert: {channel} shares cruel content. Links: {links}. Immediate removal needed under Telegram's violence policy."
]

SIGNATURES = [
    "Concerned user", "Animal lover", "Citizen reporter", "ProtectAnimals volunteer", "Anonymous witness"
]

# === ПОЧТОВЫЕ ЯЩИКИ (mail.ru) ===
# Формат в mail.txt: email:password
# Пример: mytest1@mail.ru:pass123

# === ФУНКЦИЯ ОТПРАВКИ ===
def send_complaint(sender_email, sender_pass, recipient, subject, body, attachments=None):
    try:
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = recipient
        msg['Subject'] = subject

        msg.attach(MIMEText(body, 'plain'))

        # Прикрепить скриншоты (если есть в папке attachments/)
        if attachments:
            for file_path in attachments:
                with open(file_path, "rb") as f:
                    part = MIMEBase('application', 'octet-stream')
                    part.set_payload(f.read())
                encoders.encode_base64(part)
                part.add_header(
                    'Content-Disposition',
                    f'attachment; filename= {os.path.basename(file_path)}'
                )
                msg.attach(part)

        server = smtplib.SMTP('smtp.mail.ru', 587)
        server.starttls()
        server.login(sender_email, sender_pass)
        server.send_message(msg)
        server.quit()

        now = datetime.datetime.now().strftime('%H:%M:%S')
        print(f"[{now}] УСПЕШНО: {sender_email} → {recipient}")
        return True
    except Exception as e:
        print(f"ОШИБКА: {sender_email} | {str(e)}")
        return False

# === ГЕНЕРАЦИЯ УНИКАЛЬНОЙ ЖАЛОБЫ ===
def generate_complaint():
    template = random.choice(TEMPLATES)
    links = ", ".join(random.sample(POST_LINKS, k=min(2, len(POST_LINKS))))
    body = template.format(channel=CHANNEL_LINK, links=links)
    signature = random.choice(SIGNATURES)
    return f"{body}\n\n{signature}", f"Animal Cruelty Report: {CHANNEL_LINK[:20]}..."

# === ОСНОВНОЙ ЦИКЛ ===
if name == "__main__":
    print("Запуск Animal Protector v1.0\n")

    # Загрузка аккаунтов
    senders = []
    with open("mail.txt", "r", encoding="utf-8") as f:
        for line in f.readlines():
            if ":" in line:
                email, password = line.strip().split(":", 1)
                senders.append((email, password))

    if not senders:
        print("ОШИБКА: mail.txt пустой или не найден!")
        exit()

    print(f"Загружено {len(senders)} аккаунтов. Начинаем...\n")

    # Папка со скриншотами (опционально)
    attachment_files = [f"attachments/{f}" for f in os.listdir("attachments") if f.endswith(('.png', '.jpg', '.mp4'))][:2]

    used_combinations = set()

    for sender_email, sender_pass in senders:
        for recipient in RECIPIENTS:
            # Генерация уникальной жалобы
            while True:
                body, subject = generate_complaint()
                key = (sender_email, body[:50])
                if key not in used_combinations:
                    used_combinations.add(key)
                    break

            # Отправка
            success = send_complaint(
                sender_email, sender_pass, recipient,
                subject, body, attachment_files if random.random() > 0.5 else None
            )

            if success:
                # Случайная задержка: 5–10 минут
                delay = random.randint(300, 600)
                print(f"Ожидание {delay//60} минут...")
                for _ in tqdm(range(delay), desc="Пауза"):
                    time.sleep(1)
            else:
                time.sleep(60)  # Пауза при ошибке
