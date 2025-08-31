import os
from config import settings

def check_documents():
    print("🔍 Проверка документов в папке:", settings.documents_dir)
    
    if not os.path.exists(settings.documents_dir):
        print("❌ Папка документов не существует!")
        return
        
    files = os.listdir(settings.documents_dir)
    print(f"📁 Найдено файлов: {len(files)}")
    
    for file in files:
        file_path = os.path.join(settings.documents_dir, file)
        print(f"\n📄 Файл: {file}")
        print(f"   Полный путь: {file_path}")
        print(f"   Существует: {os.path.exists(file_path)}")
        print(f"   Доступен для чтения: {os.access(file_path, os.R_OK)}")
        print(f"   Размер: {os.path.getsize(file_path) if os.path.exists(file_path) else 'N/A'} байт")
        
        # Проверяем расширение
        ext = os.path.splitext(file)[1].lower()
        print(f"   Расширение: {ext}")
        print(f"   Разрешённое расширение: {ext in settings.allowed_document_types}")

if __name__ == "__main__":
    check_documents()