INSERT INTO prompt_settings (category, name, group_name, order_index, is_active) VALUES
-- 任務類型 (Scenario)
('scenario', '🗺️ 旅遊行程視覺化 (Travel Map Generation)', 'design', 5, true),
('scenario', '🎨 AI 繪圖指令生成 (Midjourney/DALL-E Prompt Design)', 'design', 6, true),
('scenario', '📈 資訊圖表設計 (Infographic Design)', 'design', 7, true),

-- 回覆格式 (Format) - 排版與比例
('format', '16:9 旅遊攻略卡片排版 (16:9 Card-style Info)', NULL, 10, true),
('format', '1:1 社群方圖地圖 (1:1 Social Media Map)', NULL, 11, true),
('format', 'A4 細緻資訊海報 (A4 Detailed Poster)', NULL, 12, true),
('format', '9:16 直式限時動態版型 (9:16 Story Format)', NULL, 13, true),
('format', '復古資訊圖表格式 (Vintage Infographic)', NULL, 14, true),

-- 語氣與風格 (Tone) - 畫風、材質、光線、氛圍
('tone', '日系動漫風格 (Anime Style) - 鮮豔色彩與柔和光線', NULL, 10, true),
('tone', '日式手繪溫暖風格 (Warm Japanese Hand-Drawn)', NULL, 11, true),
('tone', '知名動漫 Q 版風格 (Q-Version Anime)', NULL, 12, true),
('tone', '霓虹夜景賽博龐克風 (Neon Cyberpunk Nightscape)', NULL, 13, true),
('tone', '溫馨水彩繪本風格 (Watercolor Storybook)', NULL, 14, true),
('tone', '厚塗油畫風格 (Oil Painting) - 梵谷筆觸與戲劇性光線', NULL, 15, true),
('tone', '寫實攝影風格 (Photorealistic) - 自然光與高解析度', NULL, 16, true),
('tone', '像素藝術風格 (Pixel Art) - 復古遊戲感', NULL, 17, true),
('tone', '3D 渲染風格 (3D Render) - 景深效果與細膩紋理', NULL, 18, true),
('tone', '東方水墨畫風格 (Ink Wash Painting) - 寫意留白', NULL, 19, true),
('tone', '美式漫畫風格 (Comic Book Style) - 強烈對比與網點', NULL, 20, true),

-- 限制與要求 (Constraint)
('constraint', '圖片所有標題與內容必須以「台灣精準繁體中文」標示', NULL, 10, true),
('constraint', '景點、美食、住宿、交通等標籤必須具體生動且擬真', NULL, 11, true),
('constraint', '請確保畫面比例精準符合要求 (16:9, 1:1 或 9:16)', NULL, 12, true),
('constraint', '畫面請採用「黃金比例構圖 (Golden Ratio)」', NULL, 13, true),
('constraint', '如果是地圖，必須清楚標示地點之間的移動路線與箭頭', NULL, 14, true),

-- 扮演角色 (Role)
('role', '專業旅遊插畫家 (Travel Illustrator)', '設計與其他', 10, true),
('role', '資深美術指導 (Art Director)', '設計與其他', 11, true),
('role', 'Midjourney 提詞專家 (Prompt Engineer)', '技術與開發', 12, true),
('role', '地圖視覺化設計師 (Map Data Visualizer)', '設計與其他', 13, true);
