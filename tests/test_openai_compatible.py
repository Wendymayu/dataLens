"""
测试OpenAI兼容API配置
"""
import sys
sys.path.insert(0, '..')

from agent.config import ConfigManager
from agent.agent import NL2SQLAgent

def test_config():
    """测试配置加载"""
    print("=" * 60)
    print("测试配置加载")
    print("=" * 60)

    config_manager = ConfigManager('config.json')

    print(f"Provider: {config_manager.config.model.provider}")
    print(f"Model: {config_manager.config.model.model_name}")
    print(f"Base URL: {config_manager.config.model.base_url}")
    print(f"API Key: {config_manager.config.model.api_key[:20]}...")
    print(f"Database: {config_manager.config.current_database}")
    print()

def test_simple_query():
    """测试简单查询"""
    print("=" * 60)
    print("测试简单查询")
    print("=" * 60)

    config_manager = ConfigManager('config.json')
    db_config = config_manager.get_database()

    if not db_config:
        print("错误：未找到数据库配置")
        return

    try:
        agent = NL2SQLAgent(config_manager.config.model, db_config)

        # 测试查询
        test_queries = [
            "数据库中有多少个用户？",
            "商品总数是多少？",
        ]

        for query in test_queries:
            print(f"\n问题: {query}")
            print("-" * 60)
            result = agent.query(query)
            print(f"回答: {result}")
            print()

        agent.close()
        print("✓ 测试完成")

    except Exception as e:
        print(f"✗ 错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_config()
    print()
    test_simple_query()
