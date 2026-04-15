"""Database management API router"""
from fastapi import APIRouter, HTTPException
from api.models.request import DatabaseCreateRequest
from api.models.response import DatabaseResponse
from api.services.agent_service import AgentService
from agent.config import DatabaseConfig
from agent.database import DatabaseManager
from typing import List

router = APIRouter(prefix="/api/databases", tags=["databases"])


@router.get("", response_model=List[DatabaseResponse])
async def list_databases():
    """List all configured databases"""
    agent_service = AgentService.get_instance()
    config = agent_service.config_manager.config

    result = []
    for name, db in config.databases.items():
        result.append(DatabaseResponse(
            name=name,
            host=db.host,
            port=db.port,
            user=db.user,
            database=db.database,
            is_current=(name == config.current_database)
        ))
    return result


@router.post("", response_model=DatabaseResponse)
async def add_database(request: DatabaseCreateRequest):
    """Add new database configuration"""
    agent_service = AgentService.get_instance()

    if request.name in agent_service.config_manager.config.databases:
        raise HTTPException(400, "Database already exists")

    db_config = DatabaseConfig(**request.model_dump())

    # Test connection first
    try:
        test_db = DatabaseManager(db_config)
        test_db.disconnect()
    except Exception as e:
        raise HTTPException(400, f"Connection failed: {str(e)}")

    agent_service.config_manager.add_database(request.name, db_config)

    config = agent_service.config_manager.config
    return DatabaseResponse(
        name=request.name,
        host=request.host,
        port=request.port,
        user=request.user,
        database=request.database,
        is_current=(request.name == config.current_database),
        connection_status="connected"
    )


@router.delete("/{name}")
async def remove_database(name: str):
    """Remove database configuration"""
    agent_service = AgentService.get_instance()

    if name not in agent_service.config_manager.config.databases:
        raise HTTPException(404, "Database not found")

    agent_service.config_manager.remove_database(name)
    agent_service.clear_cache(name)

    return {"status": "success"}


@router.put("/{name}/current")
async def set_current_database(name: str):
    """Set current database"""
    agent_service = AgentService.get_instance()

    if not agent_service.config_manager.set_current_database(name):
        raise HTTPException(404, "Database not found")

    # Clear agent cache for fresh connection
    agent_service.clear_cache(name)

    return {"status": "success", "current_database": name}


@router.post("/{name}/test")
async def test_database_connection(name: str):
    """Test database connection"""
    agent_service = AgentService.get_instance()
    db_config = agent_service.config_manager.get_database(name)

    if not db_config:
        raise HTTPException(404, "Database not found")

    try:
        test_db = DatabaseManager(db_config)
        success = test_db.test_connection()
        test_db.disconnect()
        return {"status": "success", "connected": success}
    except Exception as e:
        return {"status": "error", "message": str(e)}


@router.get("/{name}/schema")
async def get_database_schema(name: str):
    """Get database schema"""
    agent_service = AgentService.get_instance()
    db_config = agent_service.config_manager.get_database(name)

    if not db_config:
        raise HTTPException(404, "Database not found")

    try:
        db = DatabaseManager(db_config)
        schema = db.get_schema()
        db.disconnect()
        return {"schema": schema}
    except Exception as e:
        raise HTTPException(500, str(e))