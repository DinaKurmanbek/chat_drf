import os
import sys
import django
from docx import Document as DocxDocument  # Renamed for clarity

# This should be the path to the directory containing manage.py of your Django project.
project_root = 'C:/Users/777/Desktop/pythonProject/chat'
sys.path.append(project_root)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from chat.models import Documents

def extract_text_from_word(file_path):
    doc = DocxDocument(file_path)
    return '\n'.join(paragraph.text for paragraph in doc.paragraphs)

def populate_database(word_files_dir):
    word_files_dir = os.path.abspath(word_files_dir)
    for filename in os.listdir(word_files_dir):
        if filename.endswith('.docx') and not filename.startswith('~$'):
            full_path = os.path.join(word_files_dir, filename)
            title = os.path.splitext(filename)[0]
            try:
                content = extract_text_from_word(full_path)
                Documents.objects.get_or_create(title=title, content=content)
                print(f"Document {title} added to database.")
            except Exception as e:
                print(f"Failed to add document {title}: {e}")

if __name__ == '__main__':
    path_to_word_files = 'C:/Users/777/Desktop/words'
    populate_database(path_to_word_files)
