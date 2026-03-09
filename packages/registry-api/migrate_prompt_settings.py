import os
import json
from app import create_app, db
from app.models import PromptSetting

def seed_prompt_settings():
    app = create_app()
    with app.app_context():
        # First check if the table exists/has data
        try:
            existing_count = PromptSetting.query.count()
            if existing_count > 0:
                print(f"Prompt settings already exist ({existing_count} records). Skipping creation.")
                return
        except Exception as e:
            print("Creating prompt_settings table...")
            # If query fails, table might not exist. Let db.create_all handle it.
            db.create_all()

        print("Seeding initial prompt settings...")

        settings_to_add = []

        # Scenarios
        scenarios = [
            {'category': 'scenario', 'name': '🧠 綜合代理 (General)', 'group_name': 'general', 'order_index': 1},
            {'category': 'scenario', 'name': '💻 軟體開發 (Coding)', 'group_name': 'code', 'order_index': 2},
            {'category': 'scenario', 'name': '✍️ 文字創作 (Writing)', 'group_name': 'writing', 'order_index': 3},
            {'category': 'scenario', 'name': '📊 數據分析 (Analysis)', 'group_name': 'analysis', 'order_index': 4}
        ]
        
        # Formats
        formats = [
            '條列式清單', 
            'Mermaid 流程圖 / 架構圖語法', 
            '完整的 RESTful API 規格表', 
            'JSON 格式 (純資料，無廢話)', 
            '心智圖階層列表',
            'Markdown 完整技術文件',
            'Excel CSV 格式 (逗號分隔)'
        ]
        
        # Tones
        tones = [
            '極度精簡無廢話 (Talk is cheap, show me the code)', 
            '毒舌但一針見血 (嚴格糾正錯誤)', 
            '幼稚園老師般的耐心與鼓勵', 
            '蘇格拉底式提問 (不直接給答案，引導我思考)',
            '專業的資深技術顧問',
            '幽默風趣的脫口秀演員',
            '學術論文般嚴謹客觀'
        ]

        # Constraints
        constraints = [
            '遇到不確定的事情直接說不知道，不要幻想',
            '必須提供實際的操作範例 (Examples) 或程式碼',
            '輸出內容必須直接可複製使用，不要包含解釋性的開場白',
            '請一步一步思考 (Think step-by-step)',
            '請用繁體中文 (zh-TW) 進行所有的回覆',
            '不要使用任何格式化標籤，只需純文字',
            '確保提供的程式碼沒有使用過時或廢棄的 API'
        ]

        # Roles
        role_groups = {
            '通用與企劃': ['無指定 (由 AI 推斷最佳角色)', '企業級產品經理 (PM)', '專案管理師 (PMP)', '商業策略顧問'],
            '技術與開發': ['資深全端工程師', '系統架構師 (Architect)', '資料庫管理員 (DBA)', '資安專家', 'DevOps 工程師', '演算法工程師'],
            '寫作與內容': ['專業文案撰稿人', 'SEO 行銷專家', '社群小編', '資深技術寫手 (Technical Writer)'],
            '設計與其他': ['UI/UX 設計師', '資料科學家', '財務分析師', '精算師']
        }

        # Add all to list
        for item in scenarios:
            settings_to_add.append(PromptSetting(**item))
            
        for i, fmt in enumerate(formats):
            settings_to_add.append(PromptSetting(category='format', name=fmt, order_index=i))
            
        for i, tone in enumerate(tones):
            settings_to_add.append(PromptSetting(category='tone', name=tone, order_index=i))
            
        for i, constraint in enumerate(constraints):
            settings_to_add.append(PromptSetting(category='constraint', name=constraint, order_index=i))
            
        order_counter = 0
        for group, roles in role_groups.items():
            for role in roles:
                settings_to_add.append(PromptSetting(category='role', group_name=group, name=role, order_index=order_counter))
                order_counter += 1

        db.session.bulk_save_objects(settings_to_add)
        db.session.commit()
        print(f"Successfully added {len(settings_to_add)} prompt settings.")

if __name__ == "__main__":
    seed_prompt_settings()
