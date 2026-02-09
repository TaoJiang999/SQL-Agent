-- 商品分类数据 (50条)
USE ecommerce;
SET NAMES utf8mb4;

INSERT INTO `categories` (`name`, `parent_id`, `level`, `sort_order`, `icon_url`) VALUES
-- 一级分类 (10)
('手机数码', 0, 1, 1, 'https://icon.example.com/phone.png'),
('电脑办公', 0, 1, 2, 'https://icon.example.com/computer.png'),
('家用电器', 0, 1, 3, 'https://icon.example.com/appliance.png'),
('服饰鞋包', 0, 1, 4, 'https://icon.example.com/fashion.png'),
('美妆护肤', 0, 1, 5, 'https://icon.example.com/beauty.png'),
('食品生鲜', 0, 1, 6, 'https://icon.example.com/food.png'),
('图书音像', 0, 1, 7, 'https://icon.example.com/book.png'),
('家居家装', 0, 1, 8, 'https://icon.example.com/home.png'),
('母婴玩具', 0, 1, 9, 'https://icon.example.com/baby.png'),
('运动户外', 0, 1, 10, 'https://icon.example.com/sport.png'),
-- 二级分类-手机数码 (11-15)
('手机', 1, 2, 1, NULL),
('平板电脑', 1, 2, 2, NULL),
('智能手表', 1, 2, 3, NULL),
('耳机音响', 1, 2, 4, NULL),
('摄影摄像', 1, 2, 5, NULL),
-- 二级分类-电脑办公 (16-20)
('笔记本电脑', 2, 2, 1, NULL),
('台式电脑', 2, 2, 2, NULL),
('电脑配件', 2, 2, 3, NULL),
('办公设备', 2, 2, 4, NULL),
('网络设备', 2, 2, 5, NULL),
-- 二级分类-家用电器 (21-25)
('电视', 3, 2, 1, NULL),
('冰箱', 3, 2, 2, NULL),
('洗衣机', 3, 2, 3, NULL),
('空调', 3, 2, 4, NULL),
('小家电', 3, 2, 5, NULL),
-- 二级分类-服饰鞋包 (26-30)
('男装', 4, 2, 1, NULL),
('女装', 4, 2, 2, NULL),
('男鞋', 4, 2, 3, NULL),
('女鞋', 4, 2, 4, NULL),
('箱包', 4, 2, 5, NULL),
-- 三级分类-手机 (31-35)
('苹果手机', 11, 3, 1, NULL),
('华为手机', 11, 3, 2, NULL),
('小米手机', 11, 3, 3, NULL),
('OPPO手机', 11, 3, 4, NULL),
('vivo手机', 11, 3, 5, NULL),
-- 三级分类-笔记本电脑 (36-40)
('游戏本', 16, 3, 1, NULL),
('轻薄本', 16, 3, 2, NULL),
('商务本', 16, 3, 3, NULL),
('设计本', 16, 3, 4, NULL),
('二合一本', 16, 3, 5, NULL),
-- 三级分类-电视 (41-45)
('智能电视', 21, 3, 1, NULL),
('OLED电视', 21, 3, 2, NULL),
('激光电视', 21, 3, 3, NULL),
('投影仪', 21, 3, 4, NULL),
('电视配件', 21, 3, 5, NULL),
-- 三级分类-男装 (46-50)
('T恤', 26, 3, 1, NULL),
('衬衫', 26, 3, 2, NULL),
('裤子', 26, 3, 3, NULL),
('外套', 26, 3, 4, NULL),
('西装', 26, 3, 5, NULL);

SELECT 'Categories data inserted!' AS message;
