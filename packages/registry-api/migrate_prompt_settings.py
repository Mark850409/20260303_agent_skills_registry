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
            'Markdown 文章', 'JSON 結構化資料', '條列式清單 (Bullet points)', 
            'HTML 原始碼', '完整的報告 (Report)', '逐步教學 (Step-by-step)'
        ]
        
        # Tones
        tones = [
            '客觀冷靜', '學術嚴謹', '專業自信', '幽默風趣', 
            '熱情鼓勵', '直接了當 (無廢話)', '溫和同理', '激進具批判性'
        ]

        # Constraints
        constraints = [
            '不要使用艱澀難懂的術語', 
            '盡可能簡潔，不要有冗言贅字',
            '遇到不確定的事情直接說不知道，不要幻想',
            '必須提供實際的操作範例 (Examples) 或程式碼',
            '回覆長度限制在 500 字以內',
            '使用繁體中文 (zh-TW) 回覆',
            '輸出內容必須直接可複製使用，不要包含解釋性的開場白'
        ]

        # Roles
        role_groups = {
            '通用與策劃': ['無指定 (由 AI 推斷最佳角色)', '企業級產品經理 (PM)', '專案管理師 (PMP)', '策略顧問'],
            '技術與開發': ['資深全端工程師', '系統架構師 (Architect)', '前端 UI/UX 開發者', '資安專家', 'DevOps 工程師', '資料科學家'],
            '寫作與行銷': ['專業文案撰稿人', 'SEO 行銷專家', '社群小編', '資深編輯 / 校稿員', '公關發言人'],
            '分析與其他': ['財務分析師', '市場研究員', '心理諮商師', '語言學家 / 翻譯官']
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
