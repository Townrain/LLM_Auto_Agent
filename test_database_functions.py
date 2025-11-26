#!/usr/bin/env python3
"""
测试数据库功能脚本
用于验证数据库工具是否正常工作
"""

import sys
import os
import logging

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("DatabaseTest")

def test_database_connection():
    """测试数据库连接"""
    try:
        from database_tools import create_database_tools
        
        # 使用示例配置
        db_config = {
            'enable_database': True,
            'host': 'localhost',
            'database': 'llm_agent_db',
            'user': 'root',
            'password': '',
            'port': 3306
        }
        
        db_tools = create_database_tools(db_config)
        
        if db_tools and db_tools.db_manager:
            logger.info("✅ 数据库连接测试成功")
            return True
        else:
            logger.error("❌ 数据库工具初始化失败")
            return False
            
    except Exception as e:
        logger.error(f"❌ 数据库连接测试失败: {e}")
        return False

def test_product_stock_query():
    """测试产品库存查询"""
    try:
        from database_tools import create_database_tools
        
        db_config = {
            'enable_database': True,
            'host': 'localhost',
            'database': 'llm_agent_db',
            'user': 'root',
            'password': '',
            'port': 3306
        }
        
        db_tools = create_database_tools(db_config)
        
        if db_tools and db_tools.db_manager:
            # 测试青城山腊肉库存查询
            result = db_tools.check_product_stock("青城山腊肉")
            logger.info(f"产品库存查询结果: {result}")
            
            if result.get('status') == 'success':
                logger.info("✅ 产品库存查询成功")
                return True
            elif result.get('status') == 'not_found':
                logger.warning("⚠️  产品未找到，但查询功能正常")
                return True
            else:
                logger.error(f"❌ 产品库存查询失败: {result.get('message')}")
                return False
        else:
            logger.error("❌ 数据库工具未初始化")
            return False
            
    except Exception as e:
        logger.error(f"❌ 产品库存查询测试失败: {e}")
        return False

def test_order_status_query():
    """测试订单状态查询"""
    try:
        from database_tools import create_database_tools
        
        db_config = {
            'enable_database': True,
            'host': 'localhost',
            'database': 'llm_agent_db',
            'user': 'root',
            'password': '',
            'port': 3306
        }
        
        db_tools = create_database_tools(db_config)
        
        if db_tools and db_tools.db_manager:
            # 测试订单状态查询
            result = db_tools.check_order_status("3")
            logger.info(f"订单状态查询结果: {result}")
            
            if result.get('status') == 'success':
                logger.info("✅ 订单状态查询成功")
                return True
            elif result.get('status') == 'not_found':
                logger.warning("⚠️  订单未找到，但查询功能正常")
                return True
            else:
                logger.error(f"❌ 订单状态查询失败: {result.get('message')}")
                return False
        else:
            logger.error("❌ 数据库工具未初始化")
            return False
            
    except Exception as e:
        logger.error(f"❌ 订单状态查询测试失败: {e}")
        return False

def test_database_search():
    """测试数据库搜索功能"""
    try:
        from database_tools import create_database_tools
        
        db_config = {
            'enable_database': True,
            'host': 'localhost',
            'database': 'llm_agent_db',
            'user': 'root',
            'password': '',
            'port': 3306
        }
        
        db_tools = create_database_tools(db_config)
        
        if db_tools and db_tools.db_manager:
            # 测试安吉白茶搜索
            result = db_tools.search_knowledge_base("安吉白茶")
            logger.info(f"数据库搜索结果: {result}")
            
            if result.get('status') == 'success':
                logger.info("✅ 数据库搜索成功")
                return True
            else:
                logger.error(f"❌ 数据库搜索失败: {result.get('message')}")
                return False
        else:
            logger.error("❌ 数据库工具未初始化")
            return False
            
    except Exception as e:
        logger.error(f"❌ 数据库搜索测试失败: {e}")
        return False

def test_agent_integration():
    """测试Agent与数据库工具的集成"""
    try:
        from agent import ReactAgent
        from config_manager import ConfigManager
        
        config = ConfigManager()
        config.set('database.enabled', True)
        config.set('database.host', 'localhost')
        config.set('database.database', 'llm_agent_db')
        config.set('database.user', 'root')
        config.set('database.password', '')
        config.set('database.port', 3306)
        
        agent = ReactAgent(config)
        
        if agent and agent.db_tools:
            logger.info("✅ Agent与数据库工具集成成功")
            return True
        else:
            logger.error("❌ Agent与数据库工具集成失败")
            return False
            
    except Exception as e:
        logger.error(f"❌ Agent集成测试失败: {e}")
        return False

def main():
    """运行所有测试"""
    logger.info("🚀 开始数据库功能测试...")
    
    tests = [
        ("数据库连接", test_database_connection),
        ("产品库存查询", test_product_stock_query),
        ("订单状态查询", test_order_status_query),
        ("数据库搜索", test_database_search),
        ("Agent集成", test_agent_integration)
    ]
    
    results = []
    for test_name, test_func in tests:
        logger.info(f"\n📋 正在测试: {test_name}")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            logger.error(f"❌ 测试 {test_name} 异常: {e}")
            results.append((test_name, False))
    
    # 输出测试结果
    logger.info("\n" + "="*50)
    logger.info("📊 测试结果汇总:")
    logger.info("="*50)
    
    passed = 0
    for test_name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        logger.info(f"{test_name}: {status}")
        if result:
            passed += 1
    
    logger.info(f"\n🎯 总体结果: {passed}/{len(results)} 测试通过")
    
    if passed == len(results):
        logger.info("🎉 所有测试通过！数据库功能正常。")
    else:
        logger.warning("⚠️  部分测试失败，请检查数据库配置和连接。")

if __name__ == "__main__":
    main()