#!/usr/bin/env python3
"""
DATA INTEGRITY CHECKER
======================
Проверяет целостность данных после обработки архива.
Сравнивает оригинальные файлы с обработанными.
Показывает ЧТО именно потерялось или изменилось.
"""

import json
import os
import sys
from pathlib import Path
from collections import defaultdict
import argparse


class IntegrityChecker:
    """Проверяет целостность обработанных данных"""
    
    def __init__(self, original_dir: str, processed_dir: str):
        self.original_dir = Path(original_dir)
        self.processed_dir = Path(processed_dir)
        self.report = defaultdict(dict)
        
    def check_json_conversations(self):
        """Проверка JSON файла с диалогами"""
        print("\n" + "="*70)
        print("ПРОВЕРКА CONVERSATIONS.JSON")
        print("="*70)
        
        # Поиск оригинального файла
        original_json = None
        for root, dirs, files in os.walk(self.original_dir):
            for file in files:
                if file.lower() in ['conversations.json', 'chats.json']:
                    original_json = Path(root) / file
                    break
            if original_json:
                break
        
        if not original_json or not original_json.exists():
            print("❌ Оригинальный conversations.json НЕ НАЙДЕН")
            return False
        
        print(f"✅ Найден оригинал: {original_json.name}")
        
        # Загрузка оригинального JSON
        try:
            with open(original_json, 'r', encoding='utf-8') as f:
                original_data = json.load(f)
            
            original_size = original_json.stat().st_size
            print(f"   Размер файла: {original_size / (1024*1024):.2f} MB")
            
        except Exception as e:
            print(f"❌ Ошибка чтения оригинала: {e}")
            return False
        
        # Определяем структуру
        if isinstance(original_data, list):
            conversations = original_data
        elif isinstance(original_data, dict):
            # Пробуем найти список диалогов
            conversations = original_data.get('conversations', 
                           original_data.get('chats',
                           original_data.get('items', [])))
        else:
            print(f"❌ Неизвестная структура данных: {type(original_data)}")
            return False
        
        print(f"   Найдено диалогов: {len(conversations)}")
        
        # Подсчёт сообщений
        total_messages = 0
        total_content_size = 0
        
        for conv in conversations:
            # Подсчёт через mapping (ChatGPT формат)
            if 'mapping' in conv:
                messages = conv['mapping']
                total_messages += len(messages)
                
                # Подсчёт размера контента
                for msg_id, msg_data in messages.items():
                    if isinstance(msg_data, dict) and 'message' in msg_data:
                        message = msg_data['message']
                        if message and 'content' in message:
                            content = message.get('content', {})
                            if isinstance(content, dict) and 'parts' in content:
                                for part in content['parts']:
                                    if isinstance(part, str):
                                        total_content_size += len(part)
            
            # Подсчёт через messages (альтернативный формат)
            elif 'messages' in conv:
                messages = conv['messages']
                total_messages += len(messages)
                for msg in messages:
                    if isinstance(msg, dict) and 'content' in msg:
                        content = msg['content']
                        if isinstance(content, str):
                            total_content_size += len(content)
        
        print(f"   Всего сообщений: {total_messages}")
        print(f"   Размер текстового контента: {total_content_size / (1024*1024):.2f} MB")
        
        self.report['original'] = {
            'file_size': original_size,
            'conversations': len(conversations),
            'messages': total_messages,
            'content_size': total_content_size
        }
        
        # Проверка обработанных файлов
        print("\n" + "-"*70)
        print("ПРОВЕРКА ОБРАБОТАННЫХ ФАЙЛОВ")
        print("-"*70)
        
        individual_dir = self.processed_dir / 'chats' / 'individual'
        
        if not individual_dir.exists():
            print(f"❌ Папка с обработанными чатами не найдена: {individual_dir}")
            return False
        
        # Подсчёт обработанных файлов
        processed_files = list(individual_dir.glob('*.json'))
        print(f"✅ Найдено обработанных файлов: {len(processed_files)}")
        
        processed_total_size = 0
        processed_messages = 0
        processed_content_size = 0
        
        for file in processed_files:
            file_size = file.stat().st_size
            processed_total_size += file_size
            
            try:
                with open(file, 'r', encoding='utf-8') as f:
                    conv = json.load(f)
                
                # Подсчёт сообщений
                if 'mapping' in conv:
                    messages = conv['mapping']
                    processed_messages += len(messages)
                    
                    for msg_id, msg_data in messages.items():
                        if isinstance(msg_data, dict) and 'message' in msg_data:
                            message = msg_data['message']
                            if message and 'content' in message:
                                content = message.get('content', {})
                                if isinstance(content, dict) and 'parts' in content:
                                    for part in content['parts']:
                                        if isinstance(part, str):
                                            processed_content_size += len(part)
                
                elif 'messages' in conv:
                    messages = conv['messages']
                    processed_messages += len(messages)
                    for msg in messages:
                        if isinstance(msg, dict) and 'content' in msg:
                            content = msg['content']
                            if isinstance(content, str):
                                processed_content_size += len(content)
                
            except Exception as e:
                print(f"⚠️  Ошибка чтения {file.name}: {e}")
        
        print(f"   Общий размер файлов: {processed_total_size / (1024*1024):.2f} MB")
        print(f"   Всего сообщений: {processed_messages}")
        print(f"   Размер текстового контента: {processed_content_size / (1024*1024):.2f} MB")
        
        self.report['processed'] = {
            'file_count': len(processed_files),
            'total_size': processed_total_size,
            'messages': processed_messages,
            'content_size': processed_content_size
        }
        
        # СРАВНЕНИЕ
        print("\n" + "="*70)
        print("РЕЗУЛЬТАТЫ СРАВНЕНИЯ")
        print("="*70)
        
        conv_diff = self.report['original']['conversations'] - len(processed_files)
        msg_diff = self.report['original']['messages'] - processed_messages
        content_diff = self.report['original']['content_size'] - processed_content_size
        
        print(f"\n📊 ДИАЛОГИ:")
        print(f"   Оригинал: {self.report['original']['conversations']}")
        print(f"   Обработано: {len(processed_files)}")
        if conv_diff == 0:
            print(f"   ✅ Разница: 0 (всё ок)")
        else:
            print(f"   ❌ ПОТЕРЯНО: {conv_diff} диалогов")
        
        print(f"\n📨 СООБЩЕНИЯ:")
        print(f"   Оригинал: {self.report['original']['messages']}")
        print(f"   Обработано: {processed_messages}")
        if msg_diff == 0:
            print(f"   ✅ Разница: 0 (всё ок)")
        else:
            print(f"   ❌ ПОТЕРЯНО: {msg_diff} сообщений ({msg_diff/self.report['original']['messages']*100:.1f}%)")
        
        print(f"\n💾 ТЕКСТОВЫЙ КОНТЕНТ:")
        print(f"   Оригинал: {self.report['original']['content_size'] / (1024*1024):.2f} MB")
        print(f"   Обработано: {processed_content_size / (1024*1024):.2f} MB")
        if content_diff == 0:
            print(f"   ✅ Разница: 0 MB (всё ок)")
        else:
            print(f"   ❌ ПОТЕРЯНО: {content_diff / (1024*1024):.2f} MB ({content_diff/self.report['original']['content_size']*100:.1f}%)")
        
        print(f"\n📁 РАЗМЕР ФАЙЛОВ:")
        print(f"   Оригинал JSON: {self.report['original']['file_size'] / (1024*1024):.2f} MB")
        print(f"   Обработанные файлы: {processed_total_size / (1024*1024):.2f} MB")
        size_ratio = processed_total_size / self.report['original']['file_size']
        print(f"   Соотношение: {size_ratio:.2f}x")
        if size_ratio > 1.2:
            print(f"   ℹ️  Файлы больше из-за форматирования (indent=2)")
        elif size_ratio < 0.8:
            print(f"   ⚠️  ФАЙЛЫ МЕНЬШЕ - возможна потеря данных")
        
        return True
    
    def check_html_file(self):
        """Проверка HTML файла"""
        print("\n" + "="*70)
        print("ПРОВЕРКА HTML ФАЙЛА")
        print("="*70)
        
        # Поиск HTML файла в оригинале
        html_files = list(self.original_dir.glob('**/*.html'))
        
        if not html_files:
            print("ℹ️  HTML файл не найден")
            return True
        
        for html_file in html_files:
            print(f"\n✅ Найден: {html_file.name}")
            html_size = html_file.stat().st_size
            print(f"   Размер: {html_size / (1024*1024):.2f} MB")
            
            # Читаем содержимое
            try:
                with open(html_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Базовая статистика
                lines = content.count('\n')
                chars = len(content)
                
                print(f"   Строк: {lines:,}")
                print(f"   Символов: {chars:,}")
                
                # Проверяем есть ли структура диалогов
                if 'conversation' in content.lower() or 'message' in content.lower():
                    print(f"   ℹ️  Содержит диалоги - можно разбить на блоки")
                
            except Exception as e:
                print(f"   ⚠️  Ошибка чтения: {e}")
        
        return True
    
    def generate_report(self):
        """Генерирует финальный отчёт"""
        print("\n" + "="*70)
        print("РЕКОМЕНДАЦИИ")
        print("="*70)
        
        if not self.report.get('original') or not self.report.get('processed'):
            print("⚠️  Недостаточно данных для рекомендаций")
            return
        
        orig = self.report['original']
        proc = self.report['processed']
        
        # Проверяем потери
        msg_loss = (orig['messages'] - proc['messages']) / orig['messages'] * 100
        content_loss = (orig['content_size'] - proc['content_size']) / orig['content_size'] * 100
        
        if msg_loss > 5 or content_loss > 5:
            print("\n❌ КРИТИЧЕСКАЯ ПОТЕРЯ ДАННЫХ ОБНАРУЖЕНА!")
            print("\nПроблема:")
            print("   Скрипт ai_memory_core.py теряет данные при обработке.")
            print(f"   Потеряно сообщений: {msg_loss:.1f}%")
            print(f"   Потеряно контента: {content_loss:.1f}%")
            
            print("\nВозможные причины:")
            print("   1. Вложенные структуры mapping не полностью копируются")
            print("   2. Бинарные данные (изображения в base64) обрезаются")
            print("   3. Спецсимволы/эмодзи ломают кодировку")
            
            print("\nРешение:")
            print("   ✅ Нужна доработка скрипта с глубоким копированием")
            print("   ✅ Добавить валидацию после каждого сохранения")
            print("   ✅ Использовать json.dumps без indent для точности")
        
        elif msg_loss > 0 or content_loss > 0:
            print("\n⚠️  Небольшая потеря данных")
            print(f"   Потеряно: {msg_loss:.2f}% сообщений, {content_loss:.2f}% контента")
            print("   Возможно, это метаданные или пустые сообщения")
        
        else:
            print("\n✅ ДАННЫЕ СОХРАНЕНЫ ПОЛНОСТЬЮ")
            print("   Все диалоги и сообщения на месте")
            print("   Разница в размере файлов из-за форматирования")


def main():
    parser = argparse.ArgumentParser(
        description='Проверка целостности обработанных данных',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        '-o', '--original',
        required=True,
        help='Путь к папке с оригинальными данными (например, temp/extracted)'
    )
    
    parser.add_argument(
        '-p', '--processed',
        required=True,
        help='Путь к папке с обработанными данными'
    )
    
    args = parser.parse_args()
    
    checker = IntegrityChecker(args.original, args.processed)
    
    # Запускаем проверки
    checker.check_json_conversations()
    checker.check_html_file()
    checker.generate_report()
    
    print("\n" + "="*70)
    print("Проверка завершена")
    print("="*70 + "\n")


if __name__ == '__main__':
    main()