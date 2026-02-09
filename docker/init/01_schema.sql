-- ============================================
-- 电商系统数据库 - 表结构定义
-- ============================================

USE ecommerce;

-- 设置字符集
SET NAMES utf8mb4;
SET CHARACTER SET utf8mb4;

-- ============================================
-- 1. 用户表
-- ============================================
CREATE TABLE IF NOT EXISTS `users` (
    `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    `username` VARCHAR(50) NOT NULL COMMENT '用户名',
    `email` VARCHAR(100) NOT NULL COMMENT '邮箱',
    `password_hash` VARCHAR(255) NOT NULL COMMENT '密码哈希',
    `phone` VARCHAR(20) DEFAULT NULL COMMENT '手机号',
    `avatar_url` VARCHAR(255) DEFAULT NULL COMMENT '头像URL',
    `status` TINYINT NOT NULL DEFAULT 1 COMMENT '状态: 0禁用 1正常',
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`),
    UNIQUE KEY `uk_username` (`username`),
    UNIQUE KEY `uk_email` (`email`),
    KEY `idx_phone` (`phone`),
    KEY `idx_status` (`status`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='用户表';

-- ============================================
-- 2. 收货地址表
-- ============================================
CREATE TABLE IF NOT EXISTS `addresses` (
    `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    `user_id` BIGINT UNSIGNED NOT NULL COMMENT '用户ID',
    `receiver_name` VARCHAR(50) NOT NULL COMMENT '收货人',
    `phone` VARCHAR(20) NOT NULL COMMENT '电话',
    `province` VARCHAR(50) NOT NULL COMMENT '省',
    `city` VARCHAR(50) NOT NULL COMMENT '市',
    `district` VARCHAR(50) NOT NULL COMMENT '区',
    `detail_address` VARCHAR(255) NOT NULL COMMENT '详细地址',
    `is_default` TINYINT NOT NULL DEFAULT 0 COMMENT '是否默认: 0否 1是',
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`),
    KEY `idx_user_id` (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='收货地址表';

-- ============================================
-- 3. 商品分类表
-- ============================================
CREATE TABLE IF NOT EXISTS `categories` (
    `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    `name` VARCHAR(50) NOT NULL COMMENT '分类名称',
    `parent_id` BIGINT UNSIGNED DEFAULT 0 COMMENT '父分类ID',
    `level` TINYINT NOT NULL DEFAULT 1 COMMENT '层级: 1/2/3',
    `sort_order` INT NOT NULL DEFAULT 0 COMMENT '排序',
    `icon_url` VARCHAR(255) DEFAULT NULL COMMENT '图标URL',
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`),
    KEY `idx_parent_id` (`parent_id`),
    KEY `idx_level` (`level`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='商品分类表';

-- ============================================
-- 4. 商品表
-- ============================================
CREATE TABLE IF NOT EXISTS `products` (
    `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    `category_id` BIGINT UNSIGNED NOT NULL COMMENT '分类ID',
    `name` VARCHAR(200) NOT NULL COMMENT '商品名称',
    `description` TEXT COMMENT '商品描述',
    `price` DECIMAL(10,2) NOT NULL COMMENT '价格',
    `original_price` DECIMAL(10,2) DEFAULT NULL COMMENT '原价',
    `stock` INT NOT NULL DEFAULT 0 COMMENT '库存',
    `sales` INT NOT NULL DEFAULT 0 COMMENT '销量',
    `status` TINYINT NOT NULL DEFAULT 1 COMMENT '状态: 0下架 1上架',
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`),
    KEY `idx_category_id` (`category_id`),
    KEY `idx_status` (`status`),
    KEY `idx_price` (`price`),
    KEY `idx_sales` (`sales`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='商品表';

-- ============================================
-- 5. 商品图片表
-- ============================================
CREATE TABLE IF NOT EXISTS `product_images` (
    `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    `product_id` BIGINT UNSIGNED NOT NULL COMMENT '商品ID',
    `image_url` VARCHAR(255) NOT NULL COMMENT '图片URL',
    `sort_order` INT NOT NULL DEFAULT 0 COMMENT '排序',
    `is_main` TINYINT NOT NULL DEFAULT 0 COMMENT '是否主图: 0否 1是',
    PRIMARY KEY (`id`),
    KEY `idx_product_id` (`product_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='商品图片表';

-- ============================================
-- 6. 购物车表
-- ============================================
CREATE TABLE IF NOT EXISTS `cart_items` (
    `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    `user_id` BIGINT UNSIGNED NOT NULL COMMENT '用户ID',
    `product_id` BIGINT UNSIGNED NOT NULL COMMENT '商品ID',
    `quantity` INT NOT NULL DEFAULT 1 COMMENT '数量',
    `selected` TINYINT NOT NULL DEFAULT 1 COMMENT '是否选中: 0否 1是',
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`),
    UNIQUE KEY `uk_user_product` (`user_id`, `product_id`),
    KEY `idx_user_id` (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='购物车表';

-- ============================================
-- 7. 优惠券表
-- ============================================
CREATE TABLE IF NOT EXISTS `coupons` (
    `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    `name` VARCHAR(100) NOT NULL COMMENT '优惠券名称',
    `type` TINYINT NOT NULL DEFAULT 1 COMMENT '类型: 1满减 2折扣',
    `value` DECIMAL(10,2) NOT NULL COMMENT '面值/折扣率',
    `min_amount` DECIMAL(10,2) NOT NULL DEFAULT 0 COMMENT '最低消费',
    `start_time` DATETIME NOT NULL COMMENT '开始时间',
    `end_time` DATETIME NOT NULL COMMENT '结束时间',
    `total_count` INT NOT NULL DEFAULT 0 COMMENT '发放总量',
    `used_count` INT NOT NULL DEFAULT 0 COMMENT '已使用数量',
    `status` TINYINT NOT NULL DEFAULT 1 COMMENT '状态: 0禁用 1启用',
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`),
    KEY `idx_status` (`status`),
    KEY `idx_time` (`start_time`, `end_time`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='优惠券表';

-- ============================================
-- 8. 订单表
-- ============================================
CREATE TABLE IF NOT EXISTS `orders` (
    `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    `order_no` VARCHAR(32) NOT NULL COMMENT '订单号',
    `user_id` BIGINT UNSIGNED NOT NULL COMMENT '用户ID',
    `total_amount` DECIMAL(10,2) NOT NULL COMMENT '总金额',
    `pay_amount` DECIMAL(10,2) NOT NULL COMMENT '实付金额',
    `freight_amount` DECIMAL(10,2) NOT NULL DEFAULT 0 COMMENT '运费',
    `coupon_id` BIGINT UNSIGNED DEFAULT NULL COMMENT '优惠券ID',
    `coupon_amount` DECIMAL(10,2) NOT NULL DEFAULT 0 COMMENT '优惠金额',
    `status` TINYINT NOT NULL DEFAULT 0 COMMENT '状态: 0待付款 1待发货 2待收货 3已完成 4已取消',
    `receiver_name` VARCHAR(50) NOT NULL COMMENT '收货人',
    `receiver_phone` VARCHAR(20) NOT NULL COMMENT '电话',
    `receiver_address` VARCHAR(255) NOT NULL COMMENT '地址',
    `remark` VARCHAR(255) DEFAULT NULL COMMENT '备注',
    `pay_time` DATETIME DEFAULT NULL COMMENT '支付时间',
    `deliver_time` DATETIME DEFAULT NULL COMMENT '发货时间',
    `receive_time` DATETIME DEFAULT NULL COMMENT '收货时间',
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`),
    UNIQUE KEY `uk_order_no` (`order_no`),
    KEY `idx_user_id` (`user_id`),
    KEY `idx_status` (`status`),
    KEY `idx_created_at` (`created_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='订单表';

-- ============================================
-- 9. 订单明细表
-- ============================================
CREATE TABLE IF NOT EXISTS `order_items` (
    `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    `order_id` BIGINT UNSIGNED NOT NULL COMMENT '订单ID',
    `product_id` BIGINT UNSIGNED NOT NULL COMMENT '商品ID',
    `product_name` VARCHAR(200) NOT NULL COMMENT '商品名称快照',
    `product_image` VARCHAR(255) DEFAULT NULL COMMENT '商品图片快照',
    `price` DECIMAL(10,2) NOT NULL COMMENT '单价',
    `quantity` INT NOT NULL COMMENT '数量',
    `total_amount` DECIMAL(10,2) NOT NULL COMMENT '小计',
    PRIMARY KEY (`id`),
    KEY `idx_order_id` (`order_id`),
    KEY `idx_product_id` (`product_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='订单明细表';

-- ============================================
-- 10. 支付记录表
-- ============================================
CREATE TABLE IF NOT EXISTS `payments` (
    `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    `order_id` BIGINT UNSIGNED NOT NULL COMMENT '订单ID',
    `payment_no` VARCHAR(64) NOT NULL COMMENT '支付流水号',
    `payment_method` VARCHAR(20) NOT NULL COMMENT '支付方式: alipay/wechat/card',
    `amount` DECIMAL(10,2) NOT NULL COMMENT '支付金额',
    `status` TINYINT NOT NULL DEFAULT 0 COMMENT '状态: 0待支付 1成功 2失败',
    `paid_at` DATETIME DEFAULT NULL COMMENT '支付时间',
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`),
    UNIQUE KEY `uk_payment_no` (`payment_no`),
    KEY `idx_order_id` (`order_id`),
    KEY `idx_status` (`status`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='支付记录表';

-- ============================================
-- 11. 物流信息表
-- ============================================
CREATE TABLE IF NOT EXISTS `shipments` (
    `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    `order_id` BIGINT UNSIGNED NOT NULL COMMENT '订单ID',
    `tracking_no` VARCHAR(50) NOT NULL COMMENT '物流单号',
    `carrier` VARCHAR(50) NOT NULL COMMENT '物流公司',
    `status` TINYINT NOT NULL DEFAULT 0 COMMENT '状态: 0待发货 1运输中 2已签收',
    `shipped_at` DATETIME DEFAULT NULL COMMENT '发货时间',
    `delivered_at` DATETIME DEFAULT NULL COMMENT '签收时间',
    PRIMARY KEY (`id`),
    KEY `idx_order_id` (`order_id`),
    KEY `idx_tracking_no` (`tracking_no`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='物流信息表';

-- ============================================
-- 12. 商品评价表
-- ============================================
CREATE TABLE IF NOT EXISTS `reviews` (
    `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    `user_id` BIGINT UNSIGNED NOT NULL COMMENT '用户ID',
    `product_id` BIGINT UNSIGNED NOT NULL COMMENT '商品ID',
    `order_id` BIGINT UNSIGNED NOT NULL COMMENT '订单ID',
    `rating` TINYINT NOT NULL COMMENT '评分: 1-5',
    `content` TEXT COMMENT '评价内容',
    `images` JSON DEFAULT NULL COMMENT '评价图片',
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`),
    KEY `idx_user_id` (`user_id`),
    KEY `idx_product_id` (`product_id`),
    KEY `idx_order_id` (`order_id`),
    KEY `idx_rating` (`rating`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='商品评价表';

-- ============================================
-- 13. 用户收藏表
-- ============================================
CREATE TABLE IF NOT EXISTS `favorites` (
    `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    `user_id` BIGINT UNSIGNED NOT NULL COMMENT '用户ID',
    `product_id` BIGINT UNSIGNED NOT NULL COMMENT '商品ID',
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`),
    UNIQUE KEY `uk_user_product` (`user_id`, `product_id`),
    KEY `idx_user_id` (`user_id`),
    KEY `idx_product_id` (`product_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='用户收藏表';

-- 表结构创建完成
SELECT 'Schema created successfully!' AS message;
