import sqlite3
import os

# 使用相對路徑從 packages/registry-api 執行
db_path = "data/registry.db"

if not os.path.exists(db_path):
    print(f"找不到資料庫: {db_path}")
    exit(1)

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 檢查是否已存在 column
    cursor.execute("PRAGMA table_info(skills)")
    columns = [column[1] for column in cursor.fetchall()]
    
    if "examples" not in columns:
        print("正在新增 'examples' 欄位...")
        cursor.execute("ALTER TABLE skills ADD COLUMN examples JSON DEFAULT '[]'")
        conn.commit()
        print("成功新增欄位！")
    else:
        print("欄位 'examples' 已經存在。")
        
    conn.close()
except Exception as e:
    print(f"發生錯誤: {e}")
    exit(1)
