-- 完全兼容的乡村电商测试数据库初始化脚本
-- 解决字符编码、表结构匹配和MySQL版本兼容性问题

-- 设置字符集
SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- 删除现有表（如果存在）
DROP TABLE IF EXISTS reviews;
DROP TABLE IF EXISTS payments;
DROP TABLE IF EXISTS logistics;
DROP TABLE IF EXISTS orders;
DROP TABLE IF EXISTS products;
DROP TABLE IF EXISTS users;

-- 创建用户表
CREATE TABLE users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL,
    email VARCHAR(100),
    phone VARCHAR(20),
    address VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 插入用户数据
INSERT INTO users (username, email, phone, address) VALUES
('张三', 'zhangsan@example.com', '13800138000', '浙江省安吉县余村'),
('李四', 'lisi@example.com', '13900139000', '云南省元阳县梯田村'),
('王五', 'wangwu@example.com', '13700137000', '四川省青城山镇'),
('赵六', 'zhaoliu@example.com', '13600136000', '贵州省西江千户苗寨'),
('孙七', 'sunqi@example.com', '13500135000', '安徽省宏村'),
('周八', 'zhouba@example.com', '13400134000', '广西省阳朔县'),
('吴九', 'wujiu@example.com', '13300133000', '湖南省凤凰古城'),
('郑十', 'zhengshi@example.com', '13200132000', '江西省婺源县');

-- 创建产品表
CREATE TABLE products (
    product_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    price DECIMAL(10,2),
    stock INT,
    category VARCHAR(50),
    village VARCHAR(100),  -- 使用village而不是origin_village
    farmer VARCHAR(50),    -- 使用farmer而不是farmer_name
    harvest_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 插入产品数据
INSERT INTO products (name, description, price, stock, category, village, farmer, harvest_date) VALUES
('安吉白茶', '优质绿茶，产自浙江安吉', 280.00, 50, '茶叶', '安吉县', '张大山', '2024-03-15'),
('元阳红米', '高原红米，营养丰富', 45.00, 200, '粮食', '元阳县', '李丰收', '2024-02-20'),
('青城山腊肉', '传统工艺熏制腊肉', 88.00, 30, '肉制品', '青城山镇', '王老五', '2024-01-10'),
('苗银手镯', '手工制作苗族银饰', 320.00, 15, '手工艺品', '西江苗寨', '赵银匠', '2024-03-01'),
('宏村竹笋', '新鲜野生竹笋', 28.00, 100, '蔬菜', '宏村', '孙竹林', '2024-03-25'),
('阳朔金桔', '甜度高，果肉饱满', 35.00, 150, '水果', '阳朔县', '周果园', '2024-03-20'),
('湘西腊鱼', '湘西特色腌制腊鱼', 65.00, 40, '水产', '凤凰古城', '吴渔夫', '2024-01-15'),
('婺源皇菊', '优质皇菊，泡茶佳品', 120.00, 60, '花茶', '婺源县', '郑花农', '2024-03-10'),
('手工编织篮', '传统手工竹编篮子', 45.00, 25, '手工艺品', '安吉县', '张手艺', '2024-02-28'),
('土鸡蛋', '散养土鸡蛋，营养丰富', 25.00, 80, '禽蛋', '青城山镇', '王养殖', '2024-03-22');

-- 创建订单表
CREATE TABLE orders (
    order_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    product_id INT,
    quantity INT,
    total_price DECIMAL(10,2),
    order_status VARCHAR(30),  -- 使用order_status而不是status
    order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (product_id) REFERENCES products(product_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 插入订单数据
INSERT INTO orders (user_id, product_id, quantity, total_price, order_status) VALUES
(1, 1, 2, 560.00, '已完成'),
(2, 2, 5, 225.00, '已发货'),
(3, 3, 1, 88.00, '待支付'),
(4, 4, 1, 320.00, '已完成'),
(5, 5, 3, 84.00, '已发货'),
(6, 6, 4, 140.00, '已完成'),
(7, 7, 2, 130.00, '已取消'),
(1, 8, 1, 120.00, '待支付'),
(2, 9, 2, 90.00, '已完成'),
(3, 10, 10, 250.00, '已发货');

-- 创建物流表（完全兼容版本）
CREATE TABLE logistics (
    logistics_id INT AUTO_INCREMENT PRIMARY KEY,
    order_id INT,
    carrier VARCHAR(50) DEFAULT '中国邮政',
    tracking_number VARCHAR(100),
    logistics_status VARCHAR(50),  -- 使用logistics_status而不是status
    estimated_delivery DATE,
    actual_delivery DATE,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (order_id) REFERENCES orders(order_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 插入物流数据
INSERT INTO logistics (order_id, carrier, tracking_number, logistics_status, estimated_delivery, notes) VALUES
(1, '顺丰速运', 'SF1234567890', '已送达', '2024-04-05', '客户签收'),
(2, '中国邮政', 'YZ9876543210', '运输中', '2024-04-10', '预计明天到达'),
(5, '圆通速递', 'YT555666777', '已发货', '2024-04-08', '已揽收'),
(10, '中通快递', 'ZT111222333', '运输中', '2024-04-12', '在途');

-- 创建支付表
CREATE TABLE payments (
    payment_id INT AUTO_INCREMENT PRIMARY KEY,
    order_id INT,
    pay_method VARCHAR(50),  -- 使用pay_method而不是payment_method
    amount DECIMAL(10,2),
    pay_status VARCHAR(20),  -- 使用pay_status而不是status
    payment_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    transaction_id VARCHAR(100),
    FOREIGN KEY (order_id) REFERENCES orders(order_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 插入支付数据
INSERT INTO payments (order_id, pay_method, amount, pay_status, transaction_id) VALUES
(1, '微信支付', 560.00, '成功', 'WX202404010001'),
(2, '支付宝', 225.00, '成功', 'AL202404010002'),
(4, '银行转账', 320.00, '成功', 'BANK202404010003'),
(6, '微信支付', 140.00, '成功', 'WX202404010004'),
(9, '支付宝', 90.00, '成功', 'AL202404010005'),
(10, '货到付款', 250.00, '待支付', NULL),
(3, '微信支付', 88.00, '待支付', NULL);

-- 创建评论表
CREATE TABLE reviews (
    review_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    product_id INT,
    order_id INT,
    rating INT,
    review_text TEXT,  -- 使用review_text而不是comment
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (product_id) REFERENCES products(product_id),
    FOREIGN KEY (order_id) REFERENCES orders(order_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 插入评论数据
INSERT INTO reviews (user_id, product_id, order_id, rating, review_text) VALUES
(1, 1, 1, 5, '茶叶质量很好，包装精美，下次还会购买'),
(4, 4, 4, 4, '手镯很漂亮，做工精细，值得推荐'),
(6, 6, 6, 5, '金桔很甜，家人很喜欢，会再次购买'),
(2, 2, 2, 3, '红米口感不错，但物流有点慢'),
(5, 5, 5, 4, '竹笋很新鲜，炒菜很好吃'),
(1, 8, 8, 5, '皇菊泡茶很香，品质很好'),
(2, 9, 9, 4, '篮子做工精细，实用又美观'),
(3, 10, 10, 5, '鸡蛋很新鲜，蛋黄颜色很正'),
(7, 7, 7, 2, '商品与描述不符，申请了退款'),
(4, 3, 3, 4, '腊肉味道正宗，就是有点咸');

-- 恢复外键检查
SET FOREIGN_KEY_CHECKS = 1;

-- 数据统计查询
SELECT '用户表: ' AS 表名, COUNT(*) AS 记录数 FROM users
UNION ALL SELECT '产品表: ', COUNT(*) FROM products
UNION ALL SELECT '订单表: ', COUNT(*) FROM orders
UNION ALL SELECT '物流表: ', COUNT(*) FROM logistics
UNION ALL SELECT '支付表: ', COUNT(*) FROM payments
UNION ALL SELECT '评论表: ', COUNT(*) FROM reviews;