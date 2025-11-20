from agent import ReactAgent
from AgentConfig import AgentConfig
import os
from dotenv import load_dotenv

def main():
    """主函数 - 调试版本"""
    print("=== ReAct Agent 调试模式启动 ===")
    
    # 加载环境变量
    load_dotenv()
    
    # 检查环境变量加载
    api_key = os.getenv("DEEPSEEK_API_KEY")
    print(f"环境变量 DEEPSEEK_API_KEY 值: {api_key}")
    
    if not api_key:
        print("❌ 错误: 未找到 DeepSeek API Key")
        print("请检查以下内容:")
        print("1. 是否已创建 .env 文件")
        print("2. .env 文件是否与 run_agent.py 在同一目录")
        print("3. .env 文件中是否设置了 DEEPSEEK_API_KEY=your_actual_api_key")
        print("4. .env 文件内容示例:")
        print("   DEEPSEEK_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")
        return
    else:
        print("✅ API Key 配置正确")
    
    # 创建自定义配置
    config = AgentConfig()
    config.max_steps = 10
    config.refresh_prompt_interval = 30
    config.show_system_messages = True  # 调试模式下显示所有信息
    config.conda = "New"
    
    print(f"模型名称: {config.model_name}")
    print(f"API Base URL: {config.base_url}")
    
    # 创建并运行Agent
    agent = ReactAgent(config)
    print("✅ Agent 初始化完成，开始运行...")
    agent.run()


if __name__ == "__main__":
    main()