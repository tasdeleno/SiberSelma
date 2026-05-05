import sqlite3
import os
import glob

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'wiki.db')
WIKI_DIR = os.path.join(BASE_DIR, 'docs', 'wiki')

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    # SQLite FTS5 (Tam Metin Arama) tablosu oluştur
    c.execute('''
        CREATE VIRTUAL TABLE IF NOT EXISTS wiki_search USING fts5(
            filepath,
            content
        )
    ''')
    conn.commit()
    return conn

def ingest_all():
    conn = init_db()
    c = conn.cursor()

    print(f"'{WIKI_DIR}' içerisindeki dosyalar taranıyor ve indeksleniyor...")
    count = 0

    try:
        c.execute('BEGIN')
        c.execute('DELETE FROM wiki_search')

        for filepath in glob.glob(f"{WIKI_DIR}/**/*.md", recursive=True):
            try:
                with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    c.execute('INSERT INTO wiki_search (filepath, content) VALUES (?, ?)', (filepath, content))
                    count += 1
            except Exception as e:
                print(f"Hata: {filepath} dosyası atlandı. ({e})")

        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

    print(f"\nBasariyla {count} adet markdown (.md) dosyasi SQLite FTS5 ile indekslendi!")
    print(f"Artık SiberSelma sunucusu (server.py) milisaniyeler içerisinde cevap verebilir.")

if __name__ == "__main__":
    if not os.path.exists(WIKI_DIR):
        print(f"Hata: '{WIKI_DIR}' klasörü bulunamadı. Lütfen klasörün proje dizininde olduğundan emin olun.")
    else:
        ingest_all()
