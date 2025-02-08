import time
import requests
import feedparser
from datetime import datetime, timedelta
from telegram import Bot
import asyncio

TELEGRAM_TOKEN = '7902544546:AAFQiujDRSoVExGpu6_Y56AvFTWpupFd_Fw'  # Ваш токен
TELEGRAM_CHAT_ID = '5036565297'        # Ваш ID чата

RSS_URLS = [
    'https://www.fl.ru/rss/projects/?category=27',  # Дизайн
    'https://www.fl.ru/rss/projects/?category=28'   # Сайты
]

bot = Bot(token=TELEGRAM_TOKEN)

async def fetch_fl_jobs():
    jobs = []
    for rss_url in RSS_URLS:
        feed = feedparser.parse(rss_url)

        for entry in feed.entries:
            entry_time = datetime(*entry.published_parsed[:6])
            if datetime.now() - entry_time <= timedelta(days=1):
                job = {
                    'title': entry.title,
                    'link': entry.link,
                    'description': entry.description,
                    'author': entry.author if 'author' in entry else 'Неизвестен',
                    'published': entry_time.strftime('%Y-%m-%d %H:%M:%S')
                }
                jobs.append(job)

    print("Найдено вакансий:", len(jobs))
    for job in jobs:
        print(f"Найдена вакансия: {job['title']}, ссылка: {job['link']}")

    return jobs

async def send_jobs_to_telegram(jobs):
    for job in jobs:
        try:
            message = f"Вакансия: {job['title']}\n"
            message += f"Заказчик: {job['author']}\n"
            message += f"Описание: {job['description']}\n"
            message += f"Опубликовано: {job['published']}\n"
            message += f"Ссылка: {job['link']}\n"
            await bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)
            print(f"Отправлено сообщение для вакансии: {job['title']}")
        except Exception as e:
            print("Ошибка отправки сообщения:", e)

async def main():
    try:
        await bot.send_message(chat_id=TELEGRAM_CHAT_ID, text="Ищу, ищу, но ничего не вижу :(")
    except Exception as e:
        print("Ошибка тестового сообщения:", e)

    sent_jobs = set()

    while True:
        jobs = await fetch_fl_jobs()
        new_jobs = [job for job in jobs if job['link'] not in sent_jobs]

        if new_jobs:
            await send_jobs_to_telegram(new_jobs)
            sent_jobs.update(job['link'] for job in new_jobs)

        await asyncio.sleep(60)  # Пауза на 60 секунд

if __name__ == '__main__':
    asyncio.run(main())
