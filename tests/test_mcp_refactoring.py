"""Test MCP refactoring"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from agent.config import ConfigManager, DatabaseConfig, ModelConfig
from agent.agent import NL2SQLAgent


def test_mcp_basic():
    """Test basic MCP functionality"""
    print("Testing MCP refactoring...")

    # Create test configuration
    config_manager = ConfigManager("config.json")

    # Check if database is configured
    if not config_manager.config.databases:
        print("❌ No database configured. Please run 'python main.py' and configure a database first.")
        return False

    db_name = config_manager.config.current_database
    db_config = config_manager.get_database(db_name)

    if not db_config:
        print(f"❌ Database '{db_name}' not found")
        return False

    print(f"✓ Using database: {db_name}")
    print(f"✓ MCP enabled: {config_manager.config.use_mcp}")

    # Test with MCP enabled
    try:
        print("\n--- Testing with MCP enabled ---")
        agent = NL2SQLAgent(
            config_manager.config.model,
            db_config,
            config_manager=config_manager,
            use_mcp=True
        )

        # Test schema retrieval
        print("Testing schema retrieval...")
        schema = agent.schema
        if schema:
            print(f"✓ Schema retrieved successfully ({len(schema)} characters)")
        else:
            print("❌ Schema retrieval failed")
            return False

        agent.close()
        print("✓ MCP mode test passed")

    except Exception as e:
        print(f"❌ MCP mode test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

    # Test with MCP disabled (legacy mode)
    try:
        print("\n--- Testing with MCP disabled (legacy mode) ---")
        agent = NL2SQLAgent(
            config_manager.config.model,
            db_config,
            config_manager=config_manager,
            use_mcp=False
        )

        # Test schema retrieval
        print("Testing schema retrieval...")
        schema = agent.schema
        if schema:
            print(f"✓ Schema retrieved successfully ({len(schema)} characters)")
        else:
            print("❌ Schema retrieval failed")
            return False

        agent.close()
        print("✓ Legacy mode test passed")

    except Exception as e:
        print(f"❌ Legacy mode test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

    print("\n✅ All tests passed!")
    return True


if __name__ == "__main__":
    success = test_mcp_basic()
    sys.exit(0 if success else 1)
