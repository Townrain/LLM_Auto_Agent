-- 产品信息表 - 乡村特产和农产品数据库
CREATE TABLE IF NOT EXISTS products (
    product_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    price DECIMAL(10,2) NOT NULL,
    stock INT NOT NULL,
    category VARCHAR(50) NOT NULL,
    village_origin VARCHAR(100), -- 产地村庄
    farmer_name VARCHAR(50), -- 农户姓名
    harvest_date DATE, -- 收获日期
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 插入示例产品数据（基于真实乡村特产）
INSERT INTO products (name, description, price, stock, category, village_origin, farmer_name, harvest_date) VALUES
('安吉白茶', '产自浙江安吉的优质白茶，清香甘醇', 288.00, 50, '茶叶', '余村', '张大山', '2024-03-15'),
('元阳红米', '云南元阳梯田种植的古老红米品种', 45.00, 200, '粮食', '梯田村', '李丰收', '2024-02-20'),
('青城山腊肉', '四川青城山传统工艺熏制腊肉', 98.00, 30, '肉制品', '青城山镇', '王老五', '2024-01-10'),
('苗银首饰', '贵州苗族传统手工银饰', 350.00, 15, '手工艺品', '千户苗寨', '赵银花', '2024-03-01'),
('宏村竹编', '安徽宏村传统竹编工艺品', 120.00, 25, '手工艺品', '宏村', '孙竹匠', '2024-02-28'),
('阳朔金桔', '广西阳朔特产金桔，甜度高', 28.00, 150, '水果', '遇龙河村', '周果园', '2024-03-10'),
('凤凰姜糖', '湖南凤凰古城传统姜糖', 25.00, 100, '零食', '凤凰古城', '吴师傅', '2024-03-05'),
('婺源绿茶', '江西婺源高山绿茶', 180.00, 40, '茶叶', '江湾镇', '郑茶农', '2024-03-08'),
('农家土鸡蛋', '散养土鸡蛋，营养丰富', 15.00, 300, '禽蛋', '余村', '张养殖', '2024-03-12'),
('手工红薯粉', '传统工艺制作红薯粉条', 32.00, 80, '加工食品', '梯田村', '李加工', '2024-02-25');