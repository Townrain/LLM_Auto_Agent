-- 用户信息表 - 乡村电商用户数据库
CREATE TABLE IF NOT EXISTS users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL,
    email VARCHAR(100),
    phone VARCHAR(20),
    address TEXT NOT NULL,
    village_name VARCHAR(100), -- 所在村庄
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 插入示例用户数据（基于典型乡村地区）
INSERT INTO users (username, email, phone, address, village_name) VALUES
('张三', 'zhangsan@example.com', '13800138000', '浙江省安吉县余村123号', '余村'),
('李四', 'lisi@example.com', '13900139000', '云南省元阳县梯田村45号', '梯田村'),
('王五', 'wangwu@example.com', '13700137000', '四川省青城山镇农家乐88号', '青城山镇'),
('赵六', 'zhaoliu@example.com', '13600136000', '贵州省西江千户苗寨67号', '千户苗寨'),
('孙七', 'sunqi@example.com', '13500135000', '安徽省宏村传统文化区12号', '宏村'),
('周八', 'zhouba@example.com', '13400134000', '广西省阳朔县遇龙河村33号', '遇龙河村'),
('吴九', 'wujiu@example.com', '13300133000', '湖南省凤凰古城沱江边56号', '凤凰古城'),
('郑十', 'zhengshi@example.com', '13200132000', '江西省婺源县江湾镇78号', '江湾镇');