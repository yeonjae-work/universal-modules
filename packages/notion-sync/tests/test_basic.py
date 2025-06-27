"""Basic tests for universal-notion-sync package."""

import pytest
from unittest.mock import Mock, patch
from datetime import datetime
from enum import Enum

import universal_notion_sync


def test_package_version():
    """Test package version is accessible."""
    assert hasattr(universal_notion_sync, '__version__')
    assert universal_notion_sync.__version__ == "1.0.0"


def test_package_imports():
    """Test main imports are available."""
    # Core services
    assert hasattr(universal_notion_sync, 'UniversalNotionSyncEngine')
    assert hasattr(universal_notion_sync, 'NotionAPIClient')
    assert hasattr(universal_notion_sync, 'NotionContentProcessor')
    assert hasattr(universal_notion_sync, 'RelationDiscoveryEngine')
    assert hasattr(universal_notion_sync, 'ConfigurationManager')
    
    # Models
    assert hasattr(universal_notion_sync, 'NotionCredentials')
    assert hasattr(universal_notion_sync, 'SyncTarget')
    assert hasattr(universal_notion_sync, 'SyncConfiguration')
    assert hasattr(universal_notion_sync, 'SyncResult')
    assert hasattr(universal_notion_sync, 'BatchSyncResult')
    
    # Enums
    assert hasattr(universal_notion_sync, 'SyncStrategy')
    assert hasattr(universal_notion_sync, 'ContentFormat')
    assert hasattr(universal_notion_sync, 'RelationDiscoveryMode')


def test_sync_strategy_enum():
    """Test SyncStrategy enum values."""
    from universal_notion_sync import SyncStrategy
    
    assert isinstance(SyncStrategy.FULL_SYNC, SyncStrategy)
    assert isinstance(SyncStrategy.INCREMENTAL, SyncStrategy)
    assert isinstance(SyncStrategy.MANUAL, SyncStrategy)


def test_content_format_enum():
    """Test ContentFormat enum values."""
    from universal_notion_sync import ContentFormat
    
    assert isinstance(ContentFormat.MARKDOWN, ContentFormat)
    assert isinstance(ContentFormat.JSON, ContentFormat)


def test_relation_discovery_mode_enum():
    """Test RelationDiscoveryMode enum values."""
    from universal_notion_sync import RelationDiscoveryMode
    
    assert isinstance(RelationDiscoveryMode.DISABLED, RelationDiscoveryMode)
    assert isinstance(RelationDiscoveryMode.SHALLOW, RelationDiscoveryMode)
    assert isinstance(RelationDiscoveryMode.DEEP, RelationDiscoveryMode)
    assert isinstance(RelationDiscoveryMode.CUSTOM, RelationDiscoveryMode)


def test_notion_credentials_model():
    """Test NotionCredentials model creation."""
    from universal_notion_sync import NotionCredentials
    
    credentials = NotionCredentials(
        token="secret_token_123",
        version="2022-06-28"
    )
    
    assert credentials.token == "secret_token_123"
    assert credentials.version == "2022-06-28"


def test_sync_configuration_model():
    """Test SyncConfiguration model creation."""
    from universal_notion_sync import SyncConfiguration, SyncStrategy, ContentFormat, RelationDiscoveryMode
    
    config = SyncConfiguration(
        strategy=SyncStrategy.FULL_SYNC,
        content_format=ContentFormat.JSON,
        relation_discovery_mode=RelationDiscoveryMode.SHALLOW,
        batch_size=50,
        enable_relation_discovery=True
    )
    
    assert config.strategy == SyncStrategy.FULL_SYNC
    assert config.content_format == ContentFormat.JSON
    assert config.relation_discovery_mode == RelationDiscoveryMode.SHALLOW
    assert config.batch_size == 50
    assert config.enable_relation_discovery is True


def test_sync_target_model():
    """Test SyncTarget model creation."""
    from universal_notion_sync import SyncTarget, SyncConfiguration, SyncStrategy
    
    sync_config = SyncConfiguration(
        strategy=SyncStrategy.INCREMENTAL,
        batch_size=25
    )
    
    target = SyncTarget(
        database_id="db_123456",
        configuration=sync_config,
        name="test_target"
    )
    
    assert target.database_id == "db_123456"
    assert target.configuration.strategy == SyncStrategy.INCREMENTAL
    assert target.configuration.batch_size == 25
    assert target.name == "test_target"


def test_notion_api_client_creation():
    """Test NotionAPIClient instantiation."""
    from universal_notion_sync import NotionAPIClient, NotionCredentials
    
    credentials = NotionCredentials(token="test_token")
    client = NotionAPIClient(credentials=credentials)
    
    assert client.credentials.token == "test_token"
    assert hasattr(client, 'get_database')
    assert hasattr(client, 'query_database')
    assert hasattr(client, 'create_page')
    assert hasattr(client, 'update_page')


def test_notion_content_processor_creation():
    """Test NotionContentProcessor instantiation."""
    from universal_notion_sync import NotionContentProcessor, NotionAPIClient, NotionCredentials
    
    credentials = NotionCredentials(token="test_token")
    api_client = NotionAPIClient(credentials=credentials)
    processor = NotionContentProcessor(api_client=api_client)
    
    assert hasattr(processor, 'convert_content')
    assert hasattr(processor, 'process_blocks')
    assert hasattr(processor, 'extract_text')


def test_relation_discovery_engine_creation():
    """Test RelationDiscoveryEngine instantiation."""
    from universal_notion_sync import RelationDiscoveryEngine, NotionCredentials
    
    credentials = NotionCredentials(token="test_token")
    engine = RelationDiscoveryEngine(credentials=credentials)
    
    assert hasattr(engine, 'discover_relations')
    assert hasattr(engine, 'map_relations')
    assert hasattr(engine, 'validate_relations')


def test_universal_notion_sync_engine_creation():
    """Test UniversalNotionSyncEngine instantiation."""
    from universal_notion_sync import UniversalNotionSyncEngine, NotionCredentials
    
    credentials = NotionCredentials(token="test_token")
    engine = UniversalNotionSyncEngine(credentials=credentials)
    
    assert engine.credentials.token == "test_token"
    assert hasattr(engine, 'sync_to_target')
    assert hasattr(engine, 'batch_sync')
    assert hasattr(engine, 'sync_to_page')


def test_configuration_manager_creation():
    """Test ConfigurationManager instantiation."""
    from universal_notion_sync import ConfigurationManager
    
    manager = ConfigurationManager()
    
    # Check if it has the actual methods from the implementation
    assert hasattr(manager, 'load_configuration')


def test_notion_sync_config_creation():
    """Test NotionSyncConfig instantiation."""
    from universal_notion_sync import NotionSyncConfig
    
    config = NotionSyncConfig()
    
    assert hasattr(config, 'load_config')
    assert hasattr(config, 'get_targets')
    assert hasattr(config, 'get_credentials')


def test_sync_result_model():
    """Test SyncResult model creation."""
    from universal_notion_sync import SyncResult
    
    # Check actual field names from the model
    result = SyncResult(
        sync_id="sync_123",
        target_id="db_123", 
        status="success",
        pages_processed=10,
        timestamp=datetime.now(),
        total_pages=12
    )
    
    assert result.target_id == "db_123"
    assert result.pages_processed == 10
    assert result.total_pages == 12


def test_batch_sync_result_model():
    """Test BatchSyncResult model creation."""
    from universal_notion_sync import BatchSyncResult, SyncResult
    
    individual_result = SyncResult(
        sync_id="sync_123",
        target_id="db_123",
        status="success", 
        pages_processed=5,
        timestamp=datetime.now(),
        total_pages=5
    )
    
    batch_result = BatchSyncResult(
        batch_id="batch_123",
        results=[individual_result],
        status="completed",
        timestamp=datetime.now()
    )
    
    assert len(batch_result.results) == 1
    assert batch_result.results[0].target_id == "db_123"


def test_tasks_import_optional():
    """Test that tasks import is optional."""
    # Tasks should be importable if celery is available
    try:
        from universal_notion_sync import sync_notion_data
        # If import succeeds, check it's callable or None
        assert sync_notion_data is None or callable(sync_notion_data)
    except ImportError:
        # Import error is acceptable if celery is not installed
        pass


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
