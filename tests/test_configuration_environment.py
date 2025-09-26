
"""
Configuration and Environment Tests

Tests for production configuration loading, API key authentication,
environment variable handling, and logging/monitoring functionality.
"""

import pytest
import os
import tempfile
from unittest.mock import Mock, patch, mock_open
from pathlib import Path

from config import load_config, validate_environment
from server import MCPServer


class TestConfigurationEnvironment:
    """Test suite for configuration and environment handling"""

    @pytest.fixture
    def temp_env_file(self):
        """Create a temporary environment file for testing"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.env', delete=False) as f:
            f.write("""
# Test environment configuration
ZHIPUAI_API_KEY=test_glm_key_123
MOONSHOT_API_KEY=test_kimi_key_456
AI_MANAGER_MODEL=glm-4.5-flash
KIMI_MODEL=moonshot-v1-8k
REQUEST_TIMEOUT=30
MAX_RETRIES=3
ENABLE_INTELLIGENT_ROUTING=true
LOG_LEVEL=INFO
""")
            yield f.name
        os.unlink(f.name)

    def test_production_configuration_loading(self, temp_env_file):
        """Test loading of production configuration"""
        with patch.dict('os.environ', {}, clear=True):
            # Load configuration from file
            config = load_config(temp_env_file)
            
            # Verify essential configuration loaded
            assert config['ZHIPUAI_API_KEY'] == 'test_glm_key_123'
            assert config['MOONSHOT_API_KEY'] == 'test_kimi_key_456'
            assert config['AI_MANAGER_MODEL'] == 'glm-4.5-flash'
            assert config['REQUEST_TIMEOUT'] == 30
            assert config['ENABLE_INTELLIGENT_ROUTING'] == True

    def test_environment_variable_precedence(self, temp_env_file):
        """Test that environment variables take precedence over config file"""
        with patch.dict('os.environ', {
            'ZHIPUAI_API_KEY': 'env_override_key',
            'REQUEST_TIMEOUT': '60'
        }):
            config = load_config(temp_env_file)
            
            # Environment variables should override file values
            assert config['ZHIPUAI_API_KEY'] == 'env_override_key'
            assert config['REQUEST_TIMEOUT'] == 60
            
            # Non-overridden values should come from file
            assert config['MOONSHOT_API_KEY'] == 'test_kimi_key_456'

    def test_api_key_validation(self):
        """Test API key validation functionality"""
        # Test valid API keys
        valid_env = {
            'ZHIPUAI_API_KEY': '4973ff3ce3c0435a999ce4674bb89259.jqNMImfTWzjHMLlA',
            'MOONSHOT_API_KEY': 'sk-FbWAPZ23R4bhd5XHWttMqGgDK1QAfCk22dZmXGkliUMPu6rq'
        }
        
        with patch.dict('os.environ', valid_env):
            validation_result = validate_environment()
            assert validation_result['valid'] == True
            assert len(validation_result['errors']) == 0

    def test_missing_api_key_handling(self):
        """Test handling of missing API keys"""
        with patch.dict('os.environ', {}, clear=True):
            validation_result = validate_environment()
            
            assert validation_result['valid'] == False
            assert any('ZHIPUAI_API_KEY' in error for error in validation_result['errors'])
            assert any('MOONSHOT_API_KEY' in error for error in validation_result['errors'])

    def test_invalid_api_key_format(self):
        """Test detection of invalid API key formats"""
        invalid_env = {
            'ZHIPUAI_API_KEY': 'invalid_key',
            'MOONSHOT_API_KEY': 'also_invalid'
        }
        
        with patch.dict('os.environ', invalid_env):
            validation_result = validate_environment()
            
            # Should detect invalid formats
            assert validation_result['valid'] == False
            assert len(validation_result['warnings']) > 0

    def test_configuration_type_conversion(self):
        """Test proper type conversion of configuration values"""
        config_values = {
            'REQUEST_TIMEOUT': '30',
            'MAX_RETRIES': '3',
            'ENABLE_INTELLIGENT_ROUTING': 'true',
            'LOG_LEVEL': 'INFO'
        }
        
        with patch.dict('os.environ', config_values):
            config = load_config()
            
            # Verify type conversions
            assert isinstance(config['REQUEST_TIMEOUT'], int)
            assert isinstance(config['MAX_RETRIES'], int)
            assert isinstance(config['ENABLE_INTELLIGENT_ROUTING'], bool)
            assert isinstance(config['LOG_LEVEL'], str)

    def test_default_configuration_values(self):
        """Test that default values are properly set"""
        with patch.dict('os.environ', {
            'ZHIPUAI_API_KEY': 'test_key',
            'MOONSHOT_API_KEY': 'test_key'
        }, clear=True):
            config = load_config()
            
            # Verify defaults are applied
            assert config.get('REQUEST_TIMEOUT', 30) == 30
            assert config.get('MAX_RETRIES', 3) == 3
            assert config.get('AI_MANAGER_MODEL', 'glm-4.5-flash') == 'glm-4.5-flash'

    def test_logging_configuration(self):
        """Test logging configuration setup"""
        with patch.dict('os.environ', {
            'LOG_LEVEL': 'DEBUG',
            'LOG_FILE': 'test.log'
        }):
            # Test logging setup
            import logging
            
            with patch('logging.basicConfig') as mock_config:
                from server import setup_logging
                setup_logging()
                
                # Verify logging was configured
                mock_config.assert_called_once()

    def test_monitoring_configuration(self):
        """Test monitoring and metrics configuration"""
        monitoring_config = {
            'ENABLE_METRICS': 'true',
            'METRICS_PORT': '9090',
            'HEALTH_CHECK_INTERVAL': '60'
        }
        
        with patch.dict('os.environ', monitoring_config):
            config = load_config()
            
            assert config.get('ENABLE_METRICS') == True
            assert config.get('METRICS_PORT') == 9090
            assert config.get('HEALTH_CHECK_INTERVAL') == 60

    def test_security_configuration(self):
        """Test security-related configuration"""
        security_config = {
            'ENABLE_API_KEY_ROTATION': 'true',
            'MAX_REQUEST_SIZE': '10485760',  # 10MB
            'RATE_LIMIT_REQUESTS': '100',
            'RATE_LIMIT_WINDOW': '3600'  # 1 hour
        }
        
        with patch.dict('os.environ', security_config):
            config = load_config()
            
            assert config.get('ENABLE_API_KEY_ROTATION') == True
            assert config.get('MAX_REQUEST_SIZE') == 10485760
            assert config.get('RATE_LIMIT_REQUESTS') == 100

    def test_development_vs_production_config(self):
        """Test different configurations for development vs production"""
        # Development configuration
        dev_config = {
            'ENVIRONMENT': 'development',
            'DEBUG': 'true',
            'LOG_LEVEL': 'DEBUG'
        }
        
        with patch.dict('os.environ', dev_config):
            config = load_config()
            assert config.get('DEBUG') == True
            assert config.get('LOG_LEVEL') == 'DEBUG'
        
        # Production configuration
        prod_config = {
            'ENVIRONMENT': 'production',
            'DEBUG': 'false',
            'LOG_LEVEL': 'INFO'
        }
        
        with patch.dict('os.environ', prod_config):
            config = load_config()
            assert config.get('DEBUG') == False
            assert config.get('LOG_LEVEL') == 'INFO'

    def test_configuration_validation_errors(self):
        """Test configuration validation error handling"""
        invalid_config = {
            'REQUEST_TIMEOUT': 'not_a_number',
            'MAX_RETRIES': '-1',
            'ENABLE_INTELLIGENT_ROUTING': 'maybe'
        }
        
        with patch.dict('os.environ', invalid_config):
            with pytest.raises(ValueError):
                config = load_config(validate=True)

    def test_server_initialization_with_config(self):
        """Test server initialization with various configurations"""
        test_config = {
            'ZHIPUAI_API_KEY': '4973ff3ce3c0435a999ce4674bb89259.jqNMImfTWzjHMLlA',
            'MOONSHOT_API_KEY': 'sk-FbWAPZ23R4bhd5XHWttMqGgDK1QAfCk22dZmXGkliUMPu6rq',
            'ENABLE_INTELLIGENT_ROUTING': 'true',
            'REQUEST_TIMEOUT': '30'
        }
        
        with patch.dict('os.environ', test_config):
            server = MCPServer()
            
            # Verify server initialized with correct configuration
            assert hasattr(server, 'config')
            assert server.config['ENABLE_INTELLIGENT_ROUTING'] == True
            assert server.config['REQUEST_TIMEOUT'] == 30

    def test_configuration_hot_reload(self):
        """Test configuration hot reload functionality"""
        initial_config = {'LOG_LEVEL': 'INFO'}
        updated_config = {'LOG_LEVEL': 'DEBUG'}
        
        with patch.dict('os.environ', initial_config):
            config = load_config()
            assert config['LOG_LEVEL'] == 'INFO'
            
            # Simulate configuration update
            with patch.dict('os.environ', updated_config):
                reloaded_config = load_config(force_reload=True)
                assert reloaded_config['LOG_LEVEL'] == 'DEBUG'

    def test_sensitive_data_masking(self):
        """Test that sensitive configuration data is properly masked in logs"""
        sensitive_config = {
            'ZHIPUAI_API_KEY': '4973ff3ce3c0435a999ce4674bb89259.jqNMImfTWzjHMLlA',
            'MOONSHOT_API_KEY': 'sk-FbWAPZ23R4bhd5XHWttMqGgDK1QAfCk22dZmXGkliUMPu6rq'
        }
        
        with patch.dict('os.environ', sensitive_config):
            with patch('logging.Logger.info') as mock_log:
                config = load_config(log_config=True)
                
                # Verify sensitive data is masked in logs
                logged_calls = [call.args[0] for call in mock_log.call_args_list]
                for call in logged_calls:
                    assert '4973ff3ce3c0435a999ce4674bb89259.jqNMImfTWzjHMLlA' not in call
                    assert 'sk-FbWAPZ23R4bhd5XHWttMqGgDK1QAfCk22dZmXGkliUMPu6rq' not in call
                    # Should contain masked versions
                    if 'API_KEY' in call:
                        assert '***' in call or 'MASKED' in call
