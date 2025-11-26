-- 物流信息表 - 乡村电商物流跟踪数据库
CREATE TABLE IF NOT EXISTS logistics (
    logistics_id INT AUTO_INCREMENT PRIMARY KEY,
    order_id INT NOT NULL,
    tracking_number VARCHAR(50) UNIQUE,
    carrier VARCHAR(50) DEFAULT '中国邮政', -- 考虑到乡村地区常用物流
    status VARCHAR(30) DEFAULT 'pending', -- pending, picked_up, in_transit, out_for_delivery, delivered
    current_location VARCHAR(100),
    estimated_delivery DATE,
    actual_delivery DATE,
    notes TEXT, -- 物流备注
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (order_id) REFERENCES orders(order_id)
);

-- 插入示例物流数据
INSERT INTO logistics (order_id, tracking_number, carrier, status, current_location, estimated_delivery, actual_delivery, notes) VALUES
(1, 'YT1234567890', '圆通速递', 'delivered', '浙江省安吉县余村', '2024-03-22', '2024-03-21', '已签收，放在村口小卖部'),
(2, 'SF9876543210', '顺丰速运', 'in_transit', '昆明中转中心', '2024-03-25', NULL, '预计明天到达县城'),
(3, 'ZT555666777', '中通快递', 'picked_up', '青城山镇快递点', '2024-03-24', NULL, '已揽收，准备发往成都'),
(4, 'YD111222333', '韵达快递', 'pending', '千户苗寨', '2024-03-26', NULL, '等待支付确认'),
(5, 'ST444555666', '申通快递', 'delivered', '安徽省宏村', '2024-03-21', '2024-03-20', '国际包裹已发出'),
(6, 'YZ777888999', '中国邮政', 'out_for_delivery', '阳朔县配送站', '2024-03-23', NULL, '今日配送'),
(7, 'JD222333444', '京东物流', 'delivered', '湖南省凤凰古城', '2024-03-20', '2024-03-19', '放在古城游客中心'),
(8, 'BS666777888', '百世快递', 'cancelled', '江湾镇', '2024-03-19', NULL, '订单已取消'),
(9, 'ZT999000111', '中通快递', 'picked_up', '青城山镇', '2024-03-24', NULL, '生鲜产品优先处理'),
(10, 'YD333444555', '韵达快递', 'pending', '梯田村', '2024-03-27', NULL, '等待商品备货');