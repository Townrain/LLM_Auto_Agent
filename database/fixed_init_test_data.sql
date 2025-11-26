-- 修复版的乡村电商测试数据库初始化脚本
-- 所有表结构和数据都在一个文件中，避免路径问题

-- 1. 创建用户表
CREATE TABLE IF NOT EXISTS users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL,
    email VARCHAR(100),
    phone VARCHAR(20),
    address TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 插入用户数据
INSERT INTO users (username, email, phone, address) VALUES
('张三', 'zhangsan@example.com', '13800138000', '浙江省安吉县余村'),
('李四', 'lisi@example.com', '13900139000', '云南省元阳县梯田村'),
('王五', 'wangwu@example.com', '13700137000', '四川省青城山镇'),
('赵六', 'zhaoliu@example.com', '13600136000', '贵州省西江千户苗寨'),
('孙七', 'sunqi@example.com', '13500135000', '安徽省宏村'),
('周八', 'zhouba@example.com', '13400134000', '湖南省凤凰古城'),
('吴九', 'wujiu@example.com', '13300133000', '广西省阳朔县'),
('郑十', 'zhengshi@example.com', '13200132000', '江西省婺源县');

-- 2. 创建产品表
CREATE TABLE IF NOT EXISTS products (
    product_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    price DECIMAL(10,2),
    stock INT,
    category VARCHAR(50),
    origin_village VARCHAR(100),
    farmer_name VARCHAR(50),
    harvest_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 插入产品数据
INSERT INTO products (name, description, price, stock, category, origin_village, farmer_name, harvest_date) VALUES
('安吉白茶', '优质绿茶，产自浙江安吉', 268.00, 50, '茶叶', '安吉县余村', '张大山', '2024-03-15'),
('元阳红米', '高原红米，梯田种植', 45.00, 200, '粮食', '元阳县梯田村', '李丰收', '2024-02-20'),
('青城山腊肉', '传统工艺熏制腊肉', 88.00, 30, '肉制品', '青城山镇', '王老五', '2024-01-10'),
('苗银手镯', '手工制作苗族银饰', 320.00, 15, '手工艺品', '西江千户苗寨', '赵银匠', '2024-03-01'),
('宏村竹编', '传统竹编工艺品', 156.00, 25, '手工艺品', '安徽省宏村', '孙巧手', '2024-02-28'),
('有机土鸡蛋', '散养土鸡蛋', 28.00, 100, '禽蛋', '凤凰古城', '周养殖', '2024-03-10'),
('阳朔金桔', '新鲜金桔，酸甜可口', 35.00, 80, '水果', '阳朔县', '吴果农', '2024-03-05'),
('婺源皇菊', '特级皇菊，清热降火', 128.00, 40, '花茶', '婺源县', '郑花农', '2024-02-15'),
('手工红薯粉', '传统工艺红薯粉', 42.00, 60, '粮食', '青城山镇', '王老五', '2024-01-25'),
('野生蜂蜜', '纯天然野生蜂蜜', 98.00, 35, '蜂产品', '元阳县梯田村', '李丰收', '2024-02-28');

-- 3. 创建订单表
CREATE TABLE IF NOT EXISTS orders (
    order_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    product_id INT,
    quantity INT,
    total_price DECIMAL(10,2),
    status VARCHAR(20),
    order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (product_id) REFERENCES products(product_id)
);

-- 插入订单数据
INSERT INTO orders (user_id, product_id, quantity, total_price, status, order_date) VALUES
(1, 1, 2, 536.00, '已完成', '2024-03-01 10:30:00'),
(2, 2, 5, 225.00, '已发货', '2024-03-02 14:20:00'),
(3, 3, 1, 88.00, '已支付', '2024-03-03 09:15:00'),
(4, 4, 1, 320.00, '待支付', '2024-03-04 16:45:00'),
(5, 5, 3, 468.00, '已完成', '2024-03-05 11:20:00'),
(6, 6, 10, 280.00, '已发货', '2024-03-06 13:30:00'),
(7, 7, 2, 70.00, '已取消', '2024-03-07 15:40:00'),
(1, 8, 1, 128.00, '已完成', '2024-03-08 08:50:00'),
(2, 9, 4, 168.00, '已支付', '2024-03-09 12:25:00'),
(3, 10, 2, 196.00, '已发货', '2024-03-10 17:10:00');

-- 4. 创建物流表（修复默认值问题）
CREATE TABLE IF NOT EXISTS logistics (
    logistics_id INT AUTO_INCREMENT PRIMARY KEY,
    order_id INT,
    carrier VARCHAR(50) DEFAULT '中国邮政',  -- 修复：使用有效的默认值
    tracking_number VARCHAR(100),
    status VARCHAR(50),
    estimated_delivery DATE,
    actual_delivery DATE,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (order_id) REFERENCES orders(order_id)
);

-- 插入物流数据
INSERT INTO logistics (order_id, carrier, tracking_number, status, estimated_delivery, actual_delivery, notes) VALUES
(1, '顺丰速运', 'SF1234567890', '已送达', '2024-03-03', '2024-03-03', '放在村口小卖部'),
(2, '中国邮政', 'YZ9876543210', '运输中', '2024-03-05', NULL, '预计明天到达'),
(5, '圆通速递', 'YT555666777', '已送达', '2024-03-07', '2024-03-06', '直接交付收件人'),
(6, '中通快递', 'ZT111222333', '已揽收', '2024-03-08', NULL, '等待发货'),
(10, '韵达快递', 'YD444555666', '运输中', '2024-03-12', NULL, '山区配送可能延迟');

-- 5. 创建支付表
CREATE TABLE IF NOT EXISTS payments (
    payment_id INT AUTO_INCREMENT PRIMARY KEY,
    order_id INT,
    payment_method VARCHAR(50),
    amount DECIMAL(10,2),
    status VARCHAR(20),
    payment_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    transaction_id VARCHAR(100),
    FOREIGN KEY (order_id) REFERENCES orders(order_id)
);

-- 插入支付数据
INSERT INTO payments (order_id, payment_method, amount, status, payment_date, transaction_id) VALUES
(1, '微信支付', 536.00, '支付成功', '2024-03-01 10:35:00', 'WX202403011035001'),
(2, '支付宝', 225.00, '支付成功', '2024-03-02 14:25:00', 'AL202403021425002'),
(3, '网银转账', 88.00, '支付成功', '2024-03-03 09:20:00', 'BANK202403030920003'),
(5, '微信支付', 468.00, '支付成功', '2024-03-05 11:25:00', 'WX202403051125004'),
(6, '支付宝', 280.00, '支付成功', '2024-03-06 13:35:00', 'AL202403061335005'),
(8, '微信支付', 128.00, '支付成功', '2024-03-08 08:55:00', 'WX202403080855006'),
(9, '货到付款', 168.00, '待支付', NULL, NULL),
(10, '支付宝', 196.00, '支付成功', '2024-03-10 17:15:00', 'AL202403101715007');

-- 6. 创建评论表
CREATE TABLE IF NOT EXISTS reviews (
    review_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    product_id INT,
    order_id INT,
    rating INT CHECK (rating >= 1 AND rating <= 5),
    comment TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (product_id) REFERENCES products(product_id),
    FOREIGN KEY (order_id) REFERENCES orders(order_id)
);

-- 插入评论数据
INSERT INTO reviews (user_id, product_id, order_id, rating, comment, created_at) VALUES
(1, 1, 1, 5, '茶叶质量很好，包装精美，下次还会购买！', '2024-03-04 09:00:00'),
(1, 8, 8, 4, '皇菊味道不错，就是包装有点简单', '2024-03-09 10:30:00'),
(2, 2, 2, 5, '红米很香，是正宗的元阳红米，推荐购买', '2024-03-06 14:20:00'),
(5, 5, 5, 3, '竹编工艺不错，但有个别地方有毛刺', '2024-03-08 16:45:00'),
(6, 6, 6, 4, '土鸡蛋很新鲜，价格实惠', '2024-03-09 11:30:00'),
(3, 10, 10, 5, '蜂蜜纯正，甜度适中，非常满意', '2024-03-12 13:15:00'),
(2, 9, 9, 2, '红薯粉口感一般，不如预期的好', '2024-03-11 15:40:00'),
(4, 4, 4, 5, '苗银手镯很漂亮，工艺精湛', '2024-03-10 18:20:00'),
(7, 7, 7, 1, '金桔不新鲜，申请退款了', '2024-03-08 12:10:00'),
(5, 3, 5, 4, '腊肉味道正宗，就是有点咸', '2024-03-09 09:45:00');

-- 数据统计查询（验证导入结果）
SELECT '用户数量: ' AS info, COUNT(*) AS count FROM users
UNION ALL
SELECT '产品数量: ', COUNT(*) FROM products
UNION ALL
SELECT '订单数量: ', COUNT(*) FROM orders
UNION ALL
SELECT '物流记录: ', COUNT(*) FROM logistics
UNION ALL
SELECT '支付记录: ', COUNT(*) FROM payments
UNION ALL
SELECT '评论数量: ', COUNT(*) FROM reviews;