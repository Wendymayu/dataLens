-- ============================================
-- 电商数据库 - 建库建表及测试数据
-- ============================================

-- 创建数据库
CREATE DATABASE IF NOT EXISTS ecommerce DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE ecommerce;

-- ============================================
-- 1. 用户表
-- ============================================
DROP TABLE IF EXISTS users;
CREATE TABLE users (
    id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(50) NOT NULL UNIQUE,
    email VARCHAR(100) NOT NULL,
    phone VARCHAR(20),
    register_date DATE NOT NULL,
    level ENUM('普通会员', 'VIP会员', '黄金会员', '钻石会员') DEFAULT '普通会员',
    status ENUM('正常', '冻结') DEFAULT '正常',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户表';

-- ============================================
-- 2. 商品分类表
-- ============================================
DROP TABLE IF EXISTS categories;
CREATE TABLE categories (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(50) NOT NULL,
    parent_id INT DEFAULT 0 COMMENT '父分类ID，0表示顶级分类',
    sort_order INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='商品分类表';

-- ============================================
-- 3. 商品表
-- ============================================
DROP TABLE IF EXISTS products;
CREATE TABLE products (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(200) NOT NULL,
    category_id INT NOT NULL,
    price DECIMAL(10, 2) NOT NULL,
    stock INT NOT NULL DEFAULT 0,
    sales INT DEFAULT 0 COMMENT '销量',
    status ENUM('上架', '下架', '缺货') DEFAULT '上架',
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (category_id) REFERENCES categories(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='商品表';

-- ============================================
-- 4. 订单表
-- ============================================
DROP TABLE IF EXISTS orders;
CREATE TABLE orders (
    id INT PRIMARY KEY AUTO_INCREMENT,
    order_no VARCHAR(32) NOT NULL UNIQUE COMMENT '订单号',
    user_id INT NOT NULL,
    total_amount DECIMAL(10, 2) NOT NULL,
    status ENUM('待支付', '已支付', '已发货', '已完成', '已取消') DEFAULT '待支付',
    order_date DATETIME NOT NULL,
    pay_date DATETIME,
    ship_date DATETIME,
    complete_date DATETIME,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='订单表';

-- ============================================
-- 5. 订单明细表
-- ============================================
DROP TABLE IF EXISTS order_items;
CREATE TABLE order_items (
    id INT PRIMARY KEY AUTO_INCREMENT,
    order_id INT NOT NULL,
    product_id INT NOT NULL,
    product_name VARCHAR(200) NOT NULL COMMENT '商品名称快照',
    quantity INT NOT NULL,
    price DECIMAL(10, 2) NOT NULL COMMENT '购买时单价',
    subtotal DECIMAL(10, 2) NOT NULL COMMENT '小计',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (order_id) REFERENCES orders(id),
    FOREIGN KEY (product_id) REFERENCES products(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='订单明细表';

-- ============================================
-- 插入测试数据
-- ============================================

-- 插入用户数据
INSERT INTO users (username, email, phone, register_date, level, status) VALUES
('张三', 'zhangsan@example.com', '13800138001', '2024-01-15', 'VIP会员', '正常'),
('李四', 'lisi@example.com', '13800138002', '2024-02-20', '普通会员', '正常'),
('王五', 'wangwu@example.com', '13800138003', '2024-03-10', '黄金会员', '正常'),
('赵六', 'zhaoliu@example.com', '13800138004', '2024-01-25', '钻石会员', '正常'),
('孙七', 'sunqi@example.com', '13800138005', '2024-04-05', '普通会员', '正常'),
('周八', 'zhouba@example.com', '13800138006', '2024-02-15', 'VIP会员', '正常'),
('吴九', 'wujiu@example.com', '13800138007', '2024-03-20', '普通会员', '冻结'),
('郑十', 'zhengshi@example.com', '13800138008', '2024-01-30', '黄金会员', '正常'),
('陈十一', 'chenshiyi@example.com', '13800138009', '2024-04-10', '普通会员', '正常'),
('刘十二', 'liushier@example.com', '13800138010', '2024-02-28', 'VIP会员', '正常');

-- 插入商品分类数据
INSERT INTO categories (name, parent_id, sort_order) VALUES
('电子产品', 0, 1),
('服装鞋包', 0, 2),
('食品饮料', 0, 3),
('图书音像', 0, 4),
('家居用品', 0, 5),
('手机通讯', 1, 1),
('电脑办公', 1, 2),
('数码配件', 1, 3),
('男装', 2, 1),
('女装', 2, 2),
('休闲食品', 3, 1),
('酒水饮料', 3, 2);

-- 插入商品数据
INSERT INTO products (name, category_id, price, stock, sales, status, description) VALUES
('iPhone 15 Pro 256GB', 6, 7999.00, 50, 120, '上架', '苹果最新旗舰手机'),
('华为Mate 60 Pro', 6, 6999.00, 80, 95, '上架', '华为高端旗舰'),
('小米14 Ultra', 6, 5999.00, 100, 150, '上架', '小米影像旗舰'),
('MacBook Pro 14英寸', 7, 14999.00, 30, 45, '上架', 'M3芯片笔记本'),
('联想ThinkPad X1', 7, 9999.00, 40, 60, '上架', '商务笔记本'),
('戴尔XPS 13', 7, 8999.00, 35, 38, '上架', '轻薄本'),
('AirPods Pro 2', 8, 1899.00, 200, 280, '上架', '苹果无线耳机'),
('索尼WH-1000XM5', 8, 2399.00, 150, 95, '上架', '降噪耳机'),
('罗技MX Master 3S', 8, 699.00, 180, 210, '上架', '无线鼠标'),
('优衣库男士T恤', 9, 99.00, 500, 420, '上架', '纯棉舒适'),
('耐克运动鞋', 9, 599.00, 200, 180, '上架', '跑步鞋'),
('阿迪达斯外套', 9, 799.00, 150, 95, '上架', '运动外套'),
('ZARA连衣裙', 10, 299.00, 300, 250, '上架', '春季新款'),
('优衣库女士衬衫', 10, 199.00, 400, 320, '上架', '职业装'),
('三只松鼠坚果礼盒', 11, 128.00, 1000, 850, '上架', '混合坚果'),
('良品铺子零食大礼包', 11, 168.00, 800, 680, '上架', '休闲零食'),
('百草味肉脯', 11, 58.00, 1200, 950, '上架', '猪肉脯'),
('可口可乐 330ml*24罐', 12, 48.00, 2000, 1500, '上架', '碳酸饮料'),
('农夫山泉 550ml*24瓶', 12, 36.00, 3000, 2200, '上架', '天然水'),
('茅台飞天53度 500ml', 12, 2999.00, 50, 28, '上架', '高端白酒');

-- 插入订单数据
INSERT INTO orders (order_no, user_id, total_amount, status, order_date, pay_date, ship_date, complete_date) VALUES
('ORD202404010001', 1, 7999.00, '已完成', '2024-04-01 10:30:00', '2024-04-01 10:35:00', '2024-04-01 15:00:00', '2024-04-05 14:20:00'),
('ORD202404020001', 2, 299.00, '已完成', '2024-04-02 14:20:00', '2024-04-02 14:25:00', '2024-04-03 09:00:00', '2024-04-06 16:30:00'),
('ORD202404030001', 3, 15698.00, '已发货', '2024-04-03 09:15:00', '2024-04-03 09:20:00', '2024-04-04 10:00:00', NULL),
('ORD202404040001', 4, 2999.00, '已支付', '2024-04-04 16:45:00', '2024-04-04 16:50:00', NULL, NULL),
('ORD202404050001', 5, 176.00, '已完成', '2024-04-05 11:20:00', '2024-04-05 11:25:00', '2024-04-05 16:00:00', '2024-04-08 10:15:00'),
('ORD202404060001', 1, 1899.00, '已完成', '2024-04-06 13:30:00', '2024-04-06 13:35:00', '2024-04-07 09:00:00', '2024-04-10 15:20:00'),
('ORD202404070001', 6, 8999.00, '已完成', '2024-04-07 10:00:00', '2024-04-07 10:05:00', '2024-04-08 11:00:00', '2024-04-12 14:00:00'),
('ORD202404080001', 3, 698.00, '已取消', '2024-04-08 15:30:00', NULL, NULL, NULL),
('ORD202404090001', 8, 6999.00, '已完成', '2024-04-09 09:45:00', '2024-04-09 09:50:00', '2024-04-10 10:00:00', '2024-04-13 16:30:00'),
('ORD202404100001', 2, 599.00, '待支付', '2024-04-10 14:15:00', NULL, NULL, NULL),
('ORD202404110001', 4, 14999.00, '已完成', '2024-04-11 11:30:00', '2024-04-11 11:35:00', '2024-04-12 09:00:00', '2024-04-14 10:00:00'),
('ORD202404120001', 9, 396.00, '已完成', '2024-04-12 16:20:00', '2024-04-12 16:25:00', '2024-04-13 10:00:00', '2024-04-14 11:30:00'),
('ORD202404130001', 10, 2399.00, '已发货', '2024-04-13 10:10:00', '2024-04-13 10:15:00', '2024-04-14 09:00:00', NULL),
('ORD202404140001', 5, 128.00, '已支付', '2024-04-14 09:30:00', '2024-04-14 09:35:00', NULL, NULL);

-- 插入订单明细数据
INSERT INTO order_items (order_id, product_id, product_name, quantity, price, subtotal) VALUES
(1, 1, 'iPhone 15 Pro 256GB', 1, 7999.00, 7999.00),
(2, 13, 'ZARA连衣裙', 1, 299.00, 299.00),
(3, 4, 'MacBook Pro 14英寸', 1, 14999.00, 14999.00),
(3, 9, '罗技MX Master 3S', 1, 699.00, 699.00),
(4, 20, '茅台飞天53度 500ml', 1, 2999.00, 2999.00),
(5, 15, '三只松鼠坚果礼盒', 1, 128.00, 128.00),
(5, 18, '可口可乐 330ml*24罐', 1, 48.00, 48.00),
(6, 7, 'AirPods Pro 2', 1, 1899.00, 1899.00),
(7, 6, '戴尔XPS 13', 1, 8999.00, 8999.00),
(8, 11, '耐克运动鞋', 1, 599.00, 599.00),
(8, 10, '优衣库男士T恤', 1, 99.00, 99.00),
(9, 2, '华为Mate 60 Pro', 1, 6999.00, 6999.00),
(10, 11, '耐克运动鞋', 1, 599.00, 599.00),
(11, 4, 'MacBook Pro 14英寸', 1, 14999.00, 14999.00),
(12, 13, 'ZARA连衣裙', 1, 299.00, 299.00),
(12, 10, '优衣库男士T恤', 1, 99.00, 99.00),
(13, 8, '索尼WH-1000XM5', 1, 2399.00, 2399.00),
(14, 15, '三只松鼠坚果礼盒', 1, 128.00, 128.00);

-- ============================================
-- 创建索引以提升查询性能
-- ============================================
CREATE INDEX idx_user_level ON users(level);
CREATE INDEX idx_user_register_date ON users(register_date);
CREATE INDEX idx_product_category ON products(category_id);
CREATE INDEX idx_product_status ON products(status);
CREATE INDEX idx_order_user ON orders(user_id);
CREATE INDEX idx_order_status ON orders(status);
CREATE INDEX idx_order_date ON orders(order_date);
CREATE INDEX idx_order_item_order ON order_items(order_id);
CREATE INDEX idx_order_item_product ON order_items(product_id);

-- ============================================
-- 完成
-- ============================================
SELECT '电商数据库创建完成！' AS message;
SELECT CONCAT('共创建 ', COUNT(*), ' 个用户') AS users_count FROM users;
SELECT CONCAT('共创建 ', COUNT(*), ' 个商品分类') AS categories_count FROM categories;
SELECT CONCAT('共创建 ', COUNT(*), ' 个商品') AS products_count FROM products;
SELECT CONCAT('共创建 ', COUNT(*), ' 个订单') AS orders_count FROM orders;
SELECT CONCAT('共创建 ', COUNT(*), ' 个订单明细') AS order_items_count FROM order_items;
