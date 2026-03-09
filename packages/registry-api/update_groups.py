from app import create_app, db
from app.models import PromptSetting

app = create_app()
app.app_context().push()

settings = PromptSetting.query.all()
for s in settings:
    # --- Formats ---
    if s.category == 'format':
        if any(x in s.name for x in ['16:9', '1:1', 'A4', '9:16', '流程圖', '排版']):
            s.group_name = '特殊排版與版型 (設計與視覺)'
        elif any(x in s.name for x in ['JSON', 'RESTful', 'Excel', '原始碼']):
            s.group_name = '技術與結構化資料 (開發與工程)'
        else:
            s.group_name = '文本與報告格式 (通用)'
            
    # --- Tones ---
    elif s.category == 'tone':
        app_tones = ['動漫', '手繪', 'Q 版', '賽博龐克', '水彩', '油畫', '攝影', '像素', '3D', '水墨', '漫畫']
        if any(x in s.name for x in app_tones):
            s.group_name = '視覺與繪圖風格 (設計與視覺)'
        elif any(x in s.name for x in ['Talk is cheap', '毒舌']):
            s.group_name = '工程師語氣 (開發與工程)'
        else:
            s.group_name = '文字對話語氣 (通用)'
            
    # --- Constraints ---
    elif s.category == 'constraint':
        if any(x in s.name for x in ['比例', '構圖', '路線', '生動且擬真']):
            s.group_name = '視覺繪圖限制 (設計與視覺)'
        elif any(x in s.name for x in ['API', '註解', '命名']):
            s.group_name = '技術與開發限制 (開發與工程)'
        else:
            s.group_name = '文字與通用限制 (通用)'
            
    # --- Scenarios ---
    elif s.category == 'scenario':
        if any(x in s.name for x in ['繪圖', '設計', '視覺化', 'Midjourney']):
            s.group_name = '設計與視覺'
        elif any(x in s.name for x in ['Code', '架構', '軟體', 'API', '程式']):
            s.group_name = '開發與工程'
        else:
            s.group_name = '通用'

db.session.commit()
print('Group names updated successfully!')
