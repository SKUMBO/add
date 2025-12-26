#!/usr/bin/env python3
import os
import json

def setup_config():
    """Настройка конфигурации"""
    print("═" * 50)
    print("⚙️  НАСТРОЙКА TELEGRAM SENDER ДЛЯ TERMUX")
    print("═" * 50)
    
    print("\n📱 Для работы нужны:")
    print("1. API_ID и API_HASH с https://my.telegram.org")
    print("2. Номер телефона, привязанный к Telegram")
    
    print("\n🔐 Введите данные:")
    
    api_id = input("API_ID: ").strip()
    api_hash = input("API_HASH: ").strip()
    phone = input("Номер телефона (с кодом страны): ").strip()
    
    # Запрашиваем текст
    print("\n📝 Введите текст для отправки (Ctrl+D для завершения):")
    print("(Каждое слово будет отправлено отдельным сообщением)")
    print("=" * 50)
    
    lines = []
    try:
        while True:
            line = input()
            lines.append(line)
    except EOFError:
        pass
    
    full_text = "\n".join(lines)
    
    # Запрашиваем задержку
    while True:
        try:
            delay = float(input("\n⏱️  Задержка между сообщениями (секунды): ").strip())
            if delay < 0.1:
                print("⚠️  Минимальная задержка 0.1 секунды!")
                continue
            break
        except ValueError:
            print("❌ Введите число!")
    
    # Сохраняем конфиг
    config = {
        'API_ID': api_id,
        'API_HASH': api_hash,
        'PHONE_NUMBER': phone,
        'FULL_TEXT': full_text,
        'DELAY_SECONDS': delay
    }
    
    with open('config.json', 'w', encoding='utf-8') as f:
        json.dump(config, f, ensure_ascii=False, indent=2)
    
    print("\n✅ Конфигурация сохранена в config.json")
    print("\n📋 Для запуска выполните:")
    print("python fast_sender.py")

if __name__ == '__main__':
    setup_config()