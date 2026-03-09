-- Update Scenario group names if any are missing
UPDATE prompt_settings SET group_name = 'general' WHERE category = 'scenario' AND group_name IS NULL;

-- Update Formats
UPDATE prompt_settings SET group_name = 'design' WHERE category = 'format' AND (name LIKE '%16:9%' OR name LIKE '%1:1%' OR name LIKE '%A4%' OR name LIKE '%9:16%' OR name LIKE '%復古資訊圖表%');
UPDATE prompt_settings SET group_name = 'code' WHERE category = 'format' AND (name LIKE '%JSON%' OR name LIKE '%RESTful%' OR name LIKE '%Mermaid%');
UPDATE prompt_settings SET group_name = 'analysis' WHERE category = 'format' AND (name LIKE '%Excel%');
UPDATE prompt_settings SET group_name = 'general' WHERE category = 'format' AND group_name IS NULL;

-- Update Tones
UPDATE prompt_settings SET group_name = 'design' WHERE category = 'tone' AND (name LIKE '%動漫%' OR name LIKE '%手繪%' OR name LIKE '%賽博龐克%' OR name LIKE '%水彩%' OR name LIKE '%油畫%' OR name LIKE '%攝影%' OR name LIKE '%像素%' OR name LIKE '%3D%' OR name LIKE '%水墨%' OR name LIKE '%漫畫%');
UPDATE prompt_settings SET group_name = 'code' WHERE category = 'tone' AND (name LIKE '%Talk is cheap%' OR name LIKE '%毒舌%');
UPDATE prompt_settings SET group_name = 'general' WHERE category = 'tone' AND group_name IS NULL;

-- Update Constraints
UPDATE prompt_settings SET group_name = 'design' WHERE category = 'constraint' AND (name LIKE '%比例%' OR name LIKE '%構圖%' OR name LIKE '%路線%' OR name LIKE '%生動且擬真%');
UPDATE prompt_settings SET group_name = 'code' WHERE category = 'constraint' AND (name LIKE '%解釋性的開場白%' OR name LIKE '%API%');
UPDATE prompt_settings SET group_name = 'general' WHERE category = 'constraint' AND group_name IS NULL;
