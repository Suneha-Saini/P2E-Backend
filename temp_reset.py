import sqlite3

def reset():
    db_path = 'd:/pdf-excel/backend/bank_statement_converter.db'
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("UPDATE documents SET status='uploaded'")
    conn.commit()
    print("Database updated. Total changes:", conn.total_changes)
    conn.close()

if __name__ == '__main__':
    reset()
