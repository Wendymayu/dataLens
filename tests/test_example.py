"""
Example tests for NL2SQL Agent
Run with: pytest tests/test_example.py

Note: These are integration tests that require:
1. A running MySQL database
2. Configured API keys
3. Sample data in the database
"""

import pytest
from agent.config import ConfigManager, DatabaseConfig, ModelConfig
from agent.database import DatabaseManager
from agent.agent import NL2SQLAgent


# Sample test database configuration
TEST_DB_CONFIG = DatabaseConfig(
    name="test_db",
    host="localhost",
    port=3306,
    user="root",
    password="password",
    database="test_database"
)

TEST_MODEL_CONFIG = ModelConfig(
    provider="anthropic",
    model_name="claude-3-5-sonnet-20241022",
    api_key="your-test-api-key"
)


class TestConfigManager:
    """Test configuration management"""

    def test_add_database(self):
        """Test adding a database configuration"""
        config_mgr = ConfigManager("test_config.json")
        config_mgr.add_database("testdb", TEST_DB_CONFIG)

        assert "testdb" in config_mgr.config.databases
        assert config_mgr.config.databases["testdb"].host == "localhost"

    def test_remove_database(self):
        """Test removing a database configuration"""
        config_mgr = ConfigManager("test_config.json")
        config_mgr.add_database("testdb", TEST_DB_CONFIG)
        config_mgr.remove_database("testdb")

        assert "testdb" not in config_mgr.config.databases

    def test_switch_database(self):
        """Test switching between databases"""
        config_mgr = ConfigManager("test_config.json")
        config_mgr.add_database("db1", TEST_DB_CONFIG)
        config_mgr.add_database("db2", TEST_DB_CONFIG)

        config_mgr.set_current_database("db2")
        assert config_mgr.config.current_database == "db2"


class TestDatabaseManager:
    """Test database operations"""

    @pytest.mark.skip(reason="Requires live MySQL database")
    def test_connection(self):
        """Test database connection"""
        db_mgr = DatabaseManager(TEST_DB_CONFIG)
        assert db_mgr.test_connection() is True
        db_mgr.disconnect()

    @pytest.mark.skip(reason="Requires live MySQL database")
    def test_get_schema(self):
        """Test schema retrieval"""
        db_mgr = DatabaseManager(TEST_DB_CONFIG)
        schema = db_mgr.get_schema()

        assert "Tables:" in schema
        assert TEST_DB_CONFIG.database in schema
        db_mgr.disconnect()

    @pytest.mark.skip(reason="Requires live MySQL database")
    def test_execute_query(self):
        """Test query execution"""
        db_mgr = DatabaseManager(TEST_DB_CONFIG)
        results = db_mgr.execute_query("SELECT 1 as test")

        assert len(results) > 0
        assert results[0]["test"] == 1
        db_mgr.disconnect()


class TestAgent:
    """Test NL2SQL Agent"""

    @pytest.mark.skip(reason="Requires API key and live database")
    def test_simple_query(self):
        """Test simple natural language query"""
        agent = NL2SQLAgent(TEST_MODEL_CONFIG, TEST_DB_CONFIG)
        response = agent.query("How many records are in the users table?")

        assert response is not None
        assert len(response) > 0
        agent.close()

    @pytest.mark.skip(reason="Requires API key and live database")
    def test_complex_query(self):
        """Test complex query with joins"""
        agent = NL2SQLAgent(TEST_MODEL_CONFIG, TEST_DB_CONFIG)
        response = agent.query("Show me the top 5 users by order count")

        assert response is not None
        assert len(response) > 0
        agent.close()


# Integration test example
@pytest.mark.skip(reason="Requires full setup")
def test_end_to_end_query():
    """Test complete end-to-end flow"""
    # Setup
    config_mgr = ConfigManager("test_config.json")
    config_mgr.update_model(
        "anthropic",
        "claude-3-5-sonnet-20241022",
        "your-api-key"
    )
    config_mgr.add_database("test", TEST_DB_CONFIG)
    config_mgr.set_current_database("test")

    # Execute
    db_config = config_mgr.get_database()
    agent = NL2SQLAgent(config_mgr.config.model, db_config)
    response = agent.query("List all users")
    agent.close()

    # Verify
    assert response is not None
    assert len(response) > 0


if __name__ == "__main__":
    # Quick manual test
    print("To run tests: pytest tests/test_example.py")
    print("\nNote: Most tests are skipped and require:")
    print("  1. A running MySQL database")
    print("  2. Valid API keys")
    print("  3. Sample data in the database")
