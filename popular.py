import asyncio
import time
import os
import sys
from telethon import TelegramClient
from telethon.errors import FloodWaitError, SessionPasswordNeededError

# === НАСТРОЙКИ ===
# СПОСОБ 1: Ввести вручную
# СПОСОБ 2: Установить переменные окружения в Termux:
# export TELEGRAM_API_ID="ваш_api_id"
# export TELEGRAM_API_HASH="ваш_api_hash"
# export TELEGRAM_PHONE="ваш_номер"

# === ПОЛУЧЕНИЕ ДАННЫХ ===
def get_config():
    """Получаем настройки безопасным способом"""
    # Сначала пробуем из переменных окружения
    API_ID = os.environ.get('TELEGRAM_API_ID')
    API_HASH = os.environ.get('TELEGRAM_API_HASH')
    PHONE_NUMBER = os.environ.get('TELEGRAM_PHONE')
    
    # Если нет, запрашиваем
    if not API_ID:
        API_ID = input("Введите API_ID: ").strip()
    if not API_HASH:
        API_HASH = input("Введите API_HASH: ").strip()
    if not PHONE_NUMBER:
        PHONE_NUMBER = input("Введите номер телефона: ").strip()
    
    return API_ID, API_HASH, PHONE_NUMBER

# === ТЕКСТ ДЛЯ ОТПРАВКИ ===
# ЗАМЕНИТЕ ЭТОТ ТЕКСТ НА СВОЙ
FULL_TEXT = """Привет! Это тестовое сообщение.
Каждое слово будет отправлено отдельно.
Это пример работы скрипта."""

DELAY_SECONDS = 1.0  # Задержка между сообщениями (в секундах)


async def send_words_separately(API_ID, API_HASH, PHONE_NUMBER):
    """Отправляет каждое слово текста отдельным сообщением"""
    
    # Создаем клиента
    client = TelegramClient('session_name', int(API_ID), API_HASH)
    
    try:
        # Подключаемся
        print("Подключаемся к Telegram...")
        await client.start(phone=PHONE_NUMBER)
        print("Успешное подключение!")
        
        # Получаем список диалогов
        print("\n" + "="*50)
        print("ВАШИ ЧАТЫ:")
        print("="*50)
        
        dialogs = []
        async for dialog in client.iter_dialogs(limit=10):
            dialogs.append(dialog)
            print(f"{len(dialogs)}. {dialog.name} (ID: {dialog.id})")
        
        if not dialogs:
            print("Нет доступных чатов!")
            return
            
        # Выбираем чат
        print("\n" + "="*50)
        choice = input("Выберите номер чата (Enter для первого): ").strip()
        if choice and choice.isdigit() and 1 <= int(choice) <= len(dialogs):
            selected_chat = dialogs[int(choice)-1]
        else:
            selected_chat = dialogs[0]
            
        print(f"\nВыбран чат: {selected_chat.name}")
        
        # Подготовка слов
        words = [word for word in FULL_TEXT.split() if word.strip()]
        print(f"\nТекст содержит {len(words)} слов")
        print(f"Задержка между сообщениями: {DELAY_SECONDS} сек")
        print(f"Примерное время: {len(words) * DELAY_SECONDS / 60:.1f} минут")
        
        # Подтверждение
        print("\n" + "="*50)
        confirm = input("Начать отправку? (y/n): ").lower()
        if confirm != 'y':
            print("Отменено")
            return
        
        # Статистика
        sent_count = 0
        errors_count = 0
        start_time = time.time()
        
        print("\n" + "="*50)
        print("НАЧИНАЕМ ОТПРАВКУ...")
        print("="*50)
        
        # Отправляем слова
        for i, word in enumerate(words, 1):
            try:
                # Отправляем слово
                await client.send_message(selected_chat.id, word)
                sent_count += 1
                
                # Прогресс
                progress = (i / len(words)) * 100
                print(f"[{i:03d}/{len(words):03d}] {progress:5.1f}% -> {word}")
                
                # Задержка (кроме последнего слова)
                if i < len(words):
                    await asyncio.sleep(DELAY_SECONDS)
                    
            except FloodWaitError as e:
                # Если ограничение от Telegram
                wait_time = e.seconds
                print(f"\n⚠️ Телеграм просит подождать {wait_time} секунд")
                for remaining in range(wait_time, 0, -1):
                    print(f"\rОжидание: {remaining:03d} сек...", end="", flush=True)
                    await asyncio.sleep(1)
                print("\nПродолжаем...")
                # Пытаемся отправить снова
                await client.send_message(selected_chat.id, word)
                sent_count += 1
                await asyncio.sleep(DELAY_SECONDS)
                
            except Exception as e:
                print(f"\n✗ Ошибка при отправке: {e}")
                errors_count += 1
                await asyncio.sleep(2)  # Пауза при ошибке
        
        # Итоги
        total_time = time.time() - start_time
        print("\n" + "="*50)
        print("ОТПРАВКА ЗАВЕРШЕНА!")
        print("="*50)
        print(f"Успешно отправлено: {sent_count}/{len(words)}")
        print(f"Ошибок: {errors_count}")
        print(f"Общее время: {total_time:.1f} секунд")
        if total_time > 0:
            print(f"Скорость: {sent_count/total_time:.1f} слов/сек")
        
    except SessionPasswordNeededError:
        # Двухфакторная аутентификация
        print("\nТребуется двухфакторная аутентификация")
        password = input("Введите пароль 2FA: ")
        await client.sign_in(password=password)
        # Продолжаем
        await send_words_separately(API_ID, API_HASH, PHONE_NUMBER)
        
    except Exception as e:
        print(f"\n❌ Критическая ошибка: {e}")
        print("Проверьте подключение к интернету и данные авторизации")
        
    finally:
        try:
            await client.disconnect()
            print("\nОтключено от Telegram")
        except:
            pass


async def send_to_specific_chat(API_ID, API_HASH, PHONE_NUMBER, chat_id):
    """Отправляет в конкретный чат (если знаете ID)"""
    
    client =