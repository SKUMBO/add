import asyncio
import time
import sys
import os
from telethon import TelegramClient, events
from telethon.errors import FloodWaitError, SessionPasswordNeededError
from telethon.tl.types import InputPeerUser, InputPeerChat, InputPeerChannel

# === НАСТРОЙКИ ===
API_ID = '29303841'  # Получите на my.telegram.org
API_HASH = 'd54b82d1dd5467b2e047c1840648017d'  # Получите на my.telegram.org
PHONE_NUMBER = '+79884497935'  # Ваш номер телефона с кодом страны

# === ТЕКСТ ДЛЯ ОТПРАВКИ ===
FULL_TEXT = """Пример текста для отправки"""

DELAY_SECONDS = 1.0  # Задержка между сообщениями (в секундах)

def clear_screen():
    """Очистка экрана для Termux"""
    os.system('clear' if os.name == 'posix' else 'cls')

async def send_words_separately():
    """Отправляет каждое слово текста отдельным сообщением"""
    
    clear_screen()
    print("═" * 50)
    print("📱 TELEGRAM FAST WORD SENDER FOR TERMUX")
    print("═" * 50)
    
    # Проверяем учетные данные
    if not API_ID or not API_HASH or not PHONE_NUMBER:
        print("\n❌ Ошибка: Сначала настройте API данные!")
        print("\nКак получить API_ID и API_HASH:")
        print("1. Перейдите на https://my.telegram.org")
        print("2. Войдите в свой аккаунт Telegram")
        print("3. Создайте новое приложение")
        print("4. Скопируйте api_id и api_hash")
        return
    
    # Создаем клиента для Termux
    session_name = 'termux_session'
    client = TelegramClient(session_name, API_ID, API_HASH)
    
    try:
        print("\n🔐 Подключаемся к Telegram...")
        await client.connect()
        
        # Проверяем авторизацию
        if not await client.is_user_authorized():
            print("\n📞 Запрашиваю код авторизации...")
            await client.send_code_request(PHONE_NUMBER)
            
            code = input("\n📝 Введите код из Telegram: ").strip()
            
            try:
                await client.sign_in(PHONE_NUMBER, code)
            except SessionPasswordNeededError:
                password = input("🔑 Введите пароль 2FA: ")
                await client.sign_in(password=password)
        
        print("✅ Успешная авторизация!")
        
        # Получаем информацию о себе
        me = await client.get_me()
        print(f"👤 Вы вошли как: {me.first_name}")
        if me.username:
            print(f"   Username: @{me.username}")
        
        # Получаем диалоги
        print("\n📋 Получаю список чатов...")
        dialogs = []
        async for dialog in client.iter_dialogs(limit=20):
            dialogs.append(dialog)
        
        if not dialogs:
            print("❌ Нет доступных чатов!")
            return
        
        # Показываем список чатов
        print("\n" + "═" * 50)
        print("📞 ВАШИ ЧАТЫ:")
        print("═" * 50)
        
        for i, dialog in enumerate(dialogs, 1):
            name = dialog.name or "Без названия"
            unread = f" ({dialog.unread_count} непрочитанных)" if dialog.unread_count else ""
            print(f"{i:2}. {name}{unread}")
        
        # Выбираем чат
        print("\n" + "═" * 50)
        while True:
            try:
                choice = input("\nВыберите номер чата (Enter для первого): ").strip()
                if not choice:
                    selected_chat = dialogs[0]
                    break
                elif choice.isdigit():
                    idx = int(choice) - 1
                    if 0 <= idx < len(dialogs):
                        selected_chat = dialogs[idx]
                        break
                    else:
                        print("❌ Неверный номер!")
                else:
                    print("❌ Введите число!")
            except KeyboardInterrupt:
                print("\n\n❌ Отменено пользователем")
                return
        
        print(f"\n✅ Выбран чат: {selected_chat.name}")
        
        # Подготовка текста
        words = [word.strip() for word in FULL_TEXT.split() if word.strip()]
        if not words:
            print("❌ Нет слов для отправки!")
            return
        
        print(f"\n📊 Статистика:")
        print(f"   • Слов для отправки: {len(words)}")
        print(f"   • Задержка: {DELAY_SECONDS} сек")
        print(f"   • Примерное время: {len(words) * DELAY_SECONDS:.1f} сек")
        
        # Подтверждение
        print("\n" + "═" * 50)
        print("⚠️  ПОДТВЕРЖДЕНИЕ")
        print("═" * 50)
        print(f"Будет отправлено {len(words)} сообщений в чат:")
        print(f"«{selected_chat.name}»")
        
        confirm = input("\nПродолжить? (y/N): ").lower()
        if confirm != 'y':
            print("❌ Отменено")
            return
        
        # Статистика
        sent_count = 0
        errors_count = 0
        start_time = time.time()
        
        print("\n" + "═" * 50)
        print("🚀 НАЧИНАЕМ ОТПРАВКУ")
        print("═" * 50)
        
        # Создаем прогресс-бар
        def print_progress(current, total, speed):
            percent = (current / total) * 100
            bar_length = 30
            filled_length = int(bar_length * current // total)
            bar = '█' * filled_length + '░' * (bar_length - filled_length)
            sys.stdout.write(f'\r[{bar}] {percent:.1f}% | {current}/{total} | {speed:.1f} слов/сек')
            sys.stdout.flush()
        
        # Отправляем слова
        for i, word in enumerate(words, 1):
            try:
                await client.send_message(selected_chat.entity, word)
                sent_count += 1
                
                # Рассчитываем скорость
                elapsed = time.time() - start_time
                speed = i / elapsed if elapsed > 0 else 0
                
                # Обновляем прогресс
                print_progress(i, len(words), speed)
                
                # Задержка (кроме последнего слова)
                if i < len(words):
                    await asyncio.sleep(DELAY_SECONDS)
                    
            except FloodWaitError as e:
                print(f"\n\n⚠️  Telegram FloodWait: ждите {e.seconds} секунд")
                for remaining in range(e.seconds, 0, -1):
                    sys.stdout.write(f"\r⏳ Ожидание: {remaining} сек...")
                    sys.stdout.flush()
                    await asyncio.sleep(1)
                print("\n🔄 Продолжаем...")
                # Повторяем отправку после ожидания
                await client.send_message(selected_chat.entity, word)
                sent_count += 1
                
            except Exception as e:
                print(f"\n❌ Ошибка при отправке: {str(e)[:50]}...")
                errors_count += 1
                await asyncio.sleep(0.5)
        
        # Итоговая статистика
        total_time = time.time() - start_time
        print("\n\n" + "═" * 50)
        print("✅ ОТПРАВКА ЗАВЕРШЕНА")
        print("═" * 50)
        print(f"📊 Результаты:")
        print(f"   • Успешно отправлено: {sent_count}/{len(words)}")
        print(f"   • Ошибок: {errors_count}")
        print(f"   • Общее время: {total_time:.1f} сек")
        if total_time > 0:
            print(f"   • Средняя скорость: {sent_count/total_time:.1f} слов/сек")
        
        # Сохраняем неотправленные слова при необходимости
        if errors_count > 0:
            print("\n⚠️  Были ошибки при отправке")
            save = input("Сохранить логи? (y/N): ").lower()
            if save == 'y':
                with open('telegram_sender_log.txt', 'w', encoding='utf-8') as f:
                    f.write(f"Дата: {time.ctime()}\n")
                    f.write(f"Чат: {selected_chat.name}\n")
                    f.write(f"Отправлено: {sent_count}/{len(words)}\n")
                    f.write(f"Ошибок: {errors_count}\n")
                    f.write(f"Время: {total_time:.1f} сек\n\n")
                    f.write("Текст:\n")
                    f.write(FULL_TEXT)
                print("✅ Логи сохранены в telegram_sender_log.txt")
    
    except Exception as e:
        print(f"\n❌ Критическая ошибка: {str(e)}")
    
    finally:
        print("\n📴 Отключаемся...")
        await client.disconnect()

async def main():
    """Основная функция"""
    try:
        await send_words_separately()
    except KeyboardInterrupt:
        print("\n\n👋 Программа завершена")
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")

if __name__ == '__main__':
    # Запускаем в Termux
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n👋 Выход из программы")