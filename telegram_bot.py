import time
import requests
import feedparser
from datetime import datetime, timedelta
from telegram import Bot

TELEGRAM_TOKEN = '7902544546:AAFQiujDRSoVExGpu6_Y56AvFTWpupFd_Fw'  # Ваш токен
TELEGRAM_CHAT_ID = '5036565297'  # Ваш ID чата

RSS_URLS = [
    'https://www.fl.ru/rss/projects/?category=27',  # Дизайн
    'https://www.fl.ru/rss/projects/?category=28'   # Сайты
]

bot = Bot(token=TELEGRAM_TOKEN)

def fetch_fl_jobs():
    jobs = []
    for rss_url in RSS_URLS:
        feed = feedparser.parse(rss_url)

        for entry in feed.entries:
            # Конвертируем время из RSS в datetime
            entry_time = datetime(*entry.published_parsed[:6])
            if datetime.now() - entry_time <= timedelta(days=1):  # Вакансии за последние 24 часа
                job = {
                    'title': entry.title,
                    'link': entry.link,
                    'description': entry.description,
                    'author': entry.author if 'author' in entry else 'Неизвестен',
                    'published': entry_time.strftime('%Y-%m-%d %H:%M:%S')
                }
                jobs.append(job)

    return jobs

def send_jobs_to_telegram(jobs):
    for job in jobs:
        message = f"Вакансия: {job['title']}\n"
        message += f"Заказчик: {job['author']}\n"
        message += f"Описание: {job['description']}\n"
        message += f"Опубликовано: {job['published']}\n"
        message += f"Ссылка: {job['link']}\n"
        bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)

def main():
    sent_jobs = set()

    while True:
        jobs = fetch_fl_jobs()
        new_jobs = [job for job in jobs if job['link'] not in sent_jobs]

        if new_jobs:
            send_jobs_to_telegram(new_jobs)
            sent_jobs.update(job['link'] for job in new_jobs)

        time.sleep(60)  # Пауза на 60 секунд

if __name__ == '__main__':
    main()
