-- 用户评论表 - 乡村电商产品评价数据库
CREATE TABLE IF NOT EXISTS reviews (
    review_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    product_id INT NOT NULL,
    order_id INT NOT NULL,
    rating INT NOT NULL CHECK (rating >= 1 AND rating <= 5),
    title VARCHAR(200),
    comment TEXT,
    is_verified BOOLEAN DEFAULT TRUE, -- 是否验证购买
    helpful_count INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (product_id) REFERENCES products(product_id),
    FOREIGN KEY (order_id) REFERENCES orders(order_id)
);

-- 插入示例评论数据
INSERT INTO reviews (user_id, product_id, order_id, rating, title, comment, is_verified, helpful_count) VALUES
(1, 1, 1, 5, '安吉白茶品质超赞！', '茶叶很新鲜，泡出来香气扑鼻，包装也很精美，送人很有面子。还会回购！', TRUE, 3),
(5, 5, 5, 4, '竹编工艺不错', '手工很精细，就是价格稍微有点高，不过物有所值。', TRUE, 1),
(7, 7, 7, 5, '正宗凤凰姜糖', '味道很正宗，跟我在凤凰古城吃的一样，包装很好，没有碎。', TRUE, 2),
(6, 6, 6, 4, '阳朔金桔很甜', '金桔很新鲜，甜度适中，就是运输过程中有几个压坏了。', TRUE, 0),
(1, 8, 8, 2, '绿茶质量一般', '茶叶碎末比较多，口感也没有描述那么好，有点失望。', TRUE, 1),
(3, 9, 9, 5, '土鸡蛋很新鲜', '鸡蛋个头均匀，蛋黄颜色很正，确实是散养的，很好吃。', TRUE, 4),
(2, 2, 2, 5, '元阳红米很好吃', '红米质量很好，煮饭很香，家里人都说好吃。会长期购买。', TRUE, 2),
(5, 3, 3, 3, '腊肉味道还可以', '腊肉味道不错，就是有点咸，可能是我口味比较淡。', TRUE, 1),
(4, 4, 4, 5, '苗银首饰很漂亮', '做工很精细，银质很好，女朋友很喜欢。', TRUE, 3),
(6, 10, 10, 4, '红薯粉质量不错', '粉条很劲道，煮汤很好吃，就是包装可以再改进一下。', TRUE, 0);