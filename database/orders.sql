-- 订单信息表 - 乡村电商订单数据库
CREATE TABLE IF NOT EXISTS orders (
    order_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    product_id INT NOT NULL,
    quantity INT NOT NULL,
    unit_price DECIMAL(10,2) NOT NULL,
    total_price DECIMAL(10,2) NOT NULL,
    status VARCHAR(20) DEFAULT 'pending', -- pending, paid, shipped, completed, cancelled
    order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    notes TEXT, -- 订单备注
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (product_id) REFERENCES products(product_id)
);

-- 插入示例订单数据
INSERT INTO orders (user_id, product_id, quantity, unit_price, total_price, status, order_date, notes) VALUES
(1, 1, 2, 288.00, 576.00, 'completed', '2024-03-20 10:30:00', '送礼物用，请包装精美'),
(2, 2, 5, 45.00, 225.00, 'shipped', '2024-03-21 14:20:00', '需要真空包装'),
(3, 3, 1, 98.00, 98.00, 'paid', '2024-03-22 09:15:00', '尽快发货'),
(4, 4, 1, 350.00, 350.00, 'pending', '2024-03-22 16:45:00', ''),
(5, 5, 3, 120.00, 360.00, 'completed', '2024-03-19 11:20:00', '送国外朋友'),
(6, 6, 10, 28.00, 280.00, 'shipped', '2024-03-21 13:30:00', '挑选大果'),
(7, 7, 8, 25.00, 200.00, 'completed', '2024-03-18 15:40:00', '多放些姜糖'),
(1, 8, 1, 180.00, 180.00, 'cancelled', '2024-03-17 10:10:00', '地址写错了'),
(3, 9, 20, 15.00, 300.00, 'paid', '2024-03-23 08:50:00', '企业团购'),
(2, 10, 5, 32.00, 160.00, 'pending', '2024-03-23 12:30:00', '');