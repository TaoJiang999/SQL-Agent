-- 商品图片数据 (120条)
USE ecommerce;
SET NAMES utf8mb4;

INSERT INTO `product_images` (`product_id`, `image_url`, `sort_order`, `is_main`) VALUES
-- iPhone 15 Pro Max (product_id=1)
(1, 'https://img.example.com/iphone15promax_1.jpg', 1, 1),
(1, 'https://img.example.com/iphone15promax_2.jpg', 2, 0),
-- iPhone 15 (product_id=2)
(2, 'https://img.example.com/iphone15_1.jpg', 1, 1),
(2, 'https://img.example.com/iphone15_2.jpg', 2, 0),
-- iPhone 14 (product_id=3)
(3, 'https://img.example.com/iphone14_1.jpg', 1, 1),
(3, 'https://img.example.com/iphone14_2.jpg', 2, 0),
-- 华为Mate 60 Pro (product_id=4)
(4, 'https://img.example.com/mate60pro_1.jpg', 1, 1),
(4, 'https://img.example.com/mate60pro_2.jpg', 2, 0),
-- 华为P60 Pro (product_id=5)
(5, 'https://img.example.com/p60pro_1.jpg', 1, 1),
(5, 'https://img.example.com/p60pro_2.jpg', 2, 0),
-- 华为nova 12 (product_id=6)
(6, 'https://img.example.com/nova12_1.jpg', 1, 1),
(6, 'https://img.example.com/nova12_2.jpg', 2, 0),
-- 小米14 Ultra (product_id=7)
(7, 'https://img.example.com/mi14ultra_1.jpg', 1, 1),
(7, 'https://img.example.com/mi14ultra_2.jpg', 2, 0),
-- 小米14 (product_id=8)
(8, 'https://img.example.com/mi14_1.jpg', 1, 1),
(8, 'https://img.example.com/mi14_2.jpg', 2, 0),
-- Redmi K70 Pro (product_id=9)
(9, 'https://img.example.com/k70pro_1.jpg', 1, 1),
(9, 'https://img.example.com/k70pro_2.jpg', 2, 0),
-- 联想拯救者 (product_id=10)
(10, 'https://img.example.com/y9000p_1.jpg', 1, 1),
(10, 'https://img.example.com/y9000p_2.jpg', 2, 0),
-- ROG枪神 (product_id=11)
(11, 'https://img.example.com/roggun8_1.jpg', 1, 1),
(11, 'https://img.example.com/roggun8_2.jpg', 2, 0),
-- 机械革命 (product_id=12)
(12, 'https://img.example.com/jxgm_1.jpg', 1, 1),
(12, 'https://img.example.com/jxgm_2.jpg', 2, 0),
-- MacBook Air 15 (product_id=13)
(13, 'https://img.example.com/mbair15_1.jpg', 1, 1),
(13, 'https://img.example.com/mbair15_2.jpg', 2, 0),
-- MacBook Pro 14 (product_id=14)
(14, 'https://img.example.com/mbpro14_1.jpg', 1, 1),
(14, 'https://img.example.com/mbpro14_2.jpg', 2, 0),
-- 华为MateBook X Pro (product_id=15)
(15, 'https://img.example.com/mbxpro_1.jpg', 1, 1),
(15, 'https://img.example.com/mbxpro_2.jpg', 2, 0),
-- 小米电视 (product_id=16)
(16, 'https://img.example.com/mitv85_1.jpg', 1, 1),
(16, 'https://img.example.com/mitv85_2.jpg', 2, 0),
-- 华为智慧屏 (product_id=17)
(17, 'https://img.example.com/hwscreen_1.jpg', 1, 1),
(17, 'https://img.example.com/hwscreen_2.jpg', 2, 0),
-- TCL电视 (product_id=18)
(18, 'https://img.example.com/tcl98_1.jpg', 1, 1),
(18, 'https://img.example.com/tcl98_2.jpg', 2, 0),
-- T恤产品 (product_id=19-21)
(19, 'https://img.example.com/uniqlo_tee_1.jpg', 1, 1),
(19, 'https://img.example.com/uniqlo_tee_2.jpg', 2, 0),
(20, 'https://img.example.com/nike_tee_1.jpg', 1, 1),
(20, 'https://img.example.com/nike_tee_2.jpg', 2, 0),
(21, 'https://img.example.com/adidas_tee_1.jpg', 1, 1),
(21, 'https://img.example.com/adidas_tee_2.jpg', 2, 0),
-- 更多商品图片 (product_id=22-60)
(22, 'https://img.example.com/oppo_findx7_1.jpg', 1, 1),
(22, 'https://img.example.com/oppo_findx7_2.jpg', 2, 0),
(23, 'https://img.example.com/vivo_x100_1.jpg', 1, 1),
(23, 'https://img.example.com/vivo_x100_2.jpg', 2, 0),
(24, 'https://img.example.com/thinkpad_x1_1.jpg', 1, 1),
(24, 'https://img.example.com/thinkpad_x1_2.jpg', 2, 0),
(25, 'https://img.example.com/dell_optiplex_1.jpg', 1, 1),
(25, 'https://img.example.com/dell_optiplex_2.jpg', 2, 0),
(26, 'https://img.example.com/haier_fridge_1.jpg', 1, 1),
(26, 'https://img.example.com/haier_fridge_2.jpg', 2, 0),
(27, 'https://img.example.com/siemens_fridge_1.jpg', 1, 1),
(27, 'https://img.example.com/siemens_fridge_2.jpg', 2, 0),
(28, 'https://img.example.com/haier_washer_1.jpg', 1, 1),
(28, 'https://img.example.com/haier_washer_2.jpg', 2, 0),
(29, 'https://img.example.com/littleswan_washer_1.jpg', 1, 1),
(29, 'https://img.example.com/littleswan_washer_2.jpg', 2, 0),
(30, 'https://img.example.com/gree_ac_1.jpg', 1, 1),
(30, 'https://img.example.com/gree_ac_2.jpg', 2, 0),
(31, 'https://img.example.com/midea_ac_1.jpg', 1, 1),
(31, 'https://img.example.com/midea_ac_2.jpg', 2, 0),
(32, 'https://img.example.com/dyson_v15_1.jpg', 1, 1),
(32, 'https://img.example.com/dyson_v15_2.jpg', 2, 0),
(33, 'https://img.example.com/joyoung_kettle_1.jpg', 1, 1),
(34, 'https://img.example.com/midea_kettle_1.jpg', 1, 1),
(35, 'https://img.example.com/zara_dress_1.jpg', 1, 1),
(35, 'https://img.example.com/zara_dress_2.jpg', 2, 0),
(36, 'https://img.example.com/hm_cardigan_1.jpg', 1, 1),
(37, 'https://img.example.com/ur_blazer_1.jpg', 1, 1),
(38, 'https://img.example.com/nike_af1_1.jpg', 1, 1),
(38, 'https://img.example.com/nike_af1_2.jpg', 2, 0),
(39, 'https://img.example.com/adidas_stan_1.jpg', 1, 1),
(40, 'https://img.example.com/converse_1.jpg', 1, 1),
(41, 'https://img.example.com/belle_heel_1.jpg', 1, 1),
(42, 'https://img.example.com/skechers_1.jpg', 1, 1),
(43, 'https://img.example.com/samsonite_1.jpg', 1, 1),
(44, 'https://img.example.com/coach_bag_1.jpg', 1, 1),
(45, 'https://img.example.com/ipad_pro_1.jpg', 1, 1),
(45, 'https://img.example.com/ipad_pro_2.jpg', 2, 0),
(46, 'https://img.example.com/matepad_pro_1.jpg', 1, 1),
(47, 'https://img.example.com/watch_ultra_1.jpg', 1, 1),
(48, 'https://img.example.com/watch_gt4_1.jpg', 1, 1),
(49, 'https://img.example.com/airpods_pro_1.jpg', 1, 1),
(50, 'https://img.example.com/sony_xm5_1.jpg', 1, 1),
(51, 'https://img.example.com/nuts_gift_1.jpg', 1, 1),
(52, 'https://img.example.com/snacks_1.jpg', 1, 1),
(53, 'https://img.example.com/santi_1.jpg', 1, 1),
(54, 'https://img.example.com/book_jia_1.jpg', 1, 1),
(55, 'https://img.example.com/stroller_1.jpg', 1, 1),
(56, 'https://img.example.com/feihe_milk_1.jpg', 1, 1),
(57, 'https://img.example.com/treadmill_1.jpg', 1, 1),
(58, 'https://img.example.com/toread_jacket_1.jpg', 1, 1);

SELECT 'Product images data inserted!' AS message;
