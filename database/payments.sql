-- 支付信息表 - 乡村电商支付记录数据库
CREATE TABLE IF NOT EXISTS payments (
    payment_id INT AUTO_INCREMENT PRIMARY KEY,
    order_id INT NOT NULL,
    payment_method VARCHAR(30) NOT NULL, -- wechat, alipay, bank_transfer, cash_on_delivery
    amount DECIMAL(10,2) NOT NULL,
    status VARCHAR(20) DEFAULT 'pending', -- pending, success, failed, refunded
    transaction_id VARCHAR(100), -- 第三方支付交易号
    payment_date TIMESTAMP NULL,
    refund_date TIMESTAMP NULL,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (order_id) REFERENCES orders(order_id)
);

-- 插入示例支付数据
INSERT INTO payments (order_id, payment_method, amount, status, transaction_id, payment_date, refund_date, notes) VALUES
(1, 'alipay', 576.00, 'success', '20240320103000123456', '2024-03-20 10:35:00', NULL, '支付宝扫码支付'),
(2, 'wechat', 225.00, 'success', 'wx202403211420123456', '2024-03-21 14:25:00', NULL, '微信支付'),
(3, 'bank_transfer', 98.00, 'success', 'BT202403220915789012', '2024-03-22 09:20:00', NULL, '网银转账'),
(4, 'alipay', 350.00, 'pending', NULL, NULL, NULL, '等待用户支付'),
(5, 'wechat', 360.00, 'success', 'wx202403191120654321', '2024-03-19 11:25:00', NULL, '微信国际支付'),
(6, 'alipay', 280.00, 'success', '20240321133009876543', '2024-03-21 13:35:00', NULL, '花呗分期'),
(7, 'cash_on_delivery', 200.00, 'success', NULL, '2024-03-19 16:00:00', NULL, '货到付款'),
(8, 'wechat', 180.00, 'refunded', 'wx202403171010123456', '2024-03-17 10:15:00', '2024-03-17 14:30:00', '用户取消订单，已退款'),
(9, 'bank_transfer', 300.00, 'success', 'BT202403230850456789', '2024-03-23 08:55:00', NULL, '企业对公转账'),
(10, 'alipay', 160.00, 'pending', NULL, NULL, NULL, '等待支付确认');