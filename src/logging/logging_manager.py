"""
Centralized Logging Manager for EXAI-MCP Server
================================================

Provides structured logging with automatic context enrichment, async support,
and integration with existing monitoring infrastructure.

Architecture: Hybrid approach (dictConfig + custom enrichment)
Library: structlog (industry standard, excellent async support)

Date: 2025-10-22
Reference: EXAI consultation (Continuation: 32864286-932c-4b84-aefa-e5bd19c208bd)
"""

import os
import logging
import logging.config
import structlog
from typing import Dict, Any, Optional
from contextvars import ContextVar
from pathlib import Path

# Context variables for automatic enrichment
request_id_var: ContextVar[Optional[str]] = ContextVar('request_id', default=None)
session_id_var: ContextVar[Optional[str]] = ContextVar('session_id', default=None)
user_id_var: ContextVar[Optional[str]] = ContextVar('user_id', default=None)


class LoggingManager:
    """
    Centralized logging manager with structured logging and context enrichment.
    
    Features:
    - Structured JSON logging for production
    - Colored console output for development
    - Automatic context enrichment (request_id, session_id, user_id)
    - Environment-aware configuration (dev/production/Docker)
    - Integration with existing monitoring systems
    """
    
    def __init__(self, config_path: Optional[str] = None, environment: Optional[str] = None):
        """
        Initialize logging manager.
        
        Args:
            config_path: Optional path to custom logging configuration
            environment: Environment name (dev/production/docker), auto-detected if None
        """
        self.environment = environment or self._detect_environment()
        self.config = self._load_config(config_path)
        self._setup_logging()
    
    def _detect_environment(self) -> str:
        """Detect current environment from environment variables"""
        # Check if running in Docker
        if os.path.exists('/.dockerenv') or os.environ.get('DOCKER_CONTAINER'):
            return 'docker'
        
        # Check environment variable
        env = os.environ.get('EXAI_ENVIRONMENT', 'dev').lower()
        return env if env in ['dev', 'production', 'docker'] else 'dev'
    
    def _load_config(self, config_path: Optional[str]) -> Dict[str, Any]:
        """
        Load logging configuration.
        
        Args:
            config_path: Optional path to custom configuration file
            
        Returns:
            Logging configuration dictionary
        """
        if config_path and os.path.exists(config_path):
            # Load custom configuration (future enhancement)
            pass
        
        # Use environment-specific defaults
        if self.environment == 'production':
            return self._get_production_config()
        elif self.environment == 'docker':
            return self._get_docker_config()
        else:
            return self._get_dev_config()
    
    def _get_dev_config(self) -> Dict[str, Any]:
        """Development configuration with colored console output"""
        return {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "json": {
                    "()": structlog.stdlib.ProcessorFormatter,
                    "processor": structlog.processors.JSONRenderer(),
                },
                "console": {
                    "()": structlog.dev.ConsoleRenderer,
                    "colors": True,
                }
            },
            "handlers": {
                "console": {
                    "class": "logging.StreamHandler",
                    "formatter": "console",
                    "level": "DEBUG"
                },
                "file": {
                    "class": "logging.handlers.RotatingFileHandler",
                    "filename": "logs/dev-exai-mcp.log",
                    "maxBytes": 10485760,  # 10MB
                    "backupCount": 3,
                    "formatter": "json",
                    "level": "DEBUG"
                }
            },
            "loggers": {
                "": {
                    "handlers": ["console", "file"],
                    "level": "DEBUG",
                    "propagate": False
                }
            }
        }
    
    def _get_production_config(self) -> Dict[str, Any]:
        """Production configuration with JSON logging"""
        return {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "json": {
                    "()": structlog.stdlib.ProcessorFormatter,
                    "processor": structlog.processors.JSONRenderer(),
                }
            },
            "handlers": {
                "console": {
                    "class": "logging.StreamHandler",
                    "formatter": "json",
                    "level": "INFO"
                },
                "file": {
                    "class": "logging.handlers.RotatingFileHandler",
                    "filename": "logs/prod-exai-mcp.log",
                    "maxBytes": 52428800,  # 50MB
                    "backupCount": 10,
                    "formatter": "json",
                    "level": "INFO"
                }
            },
            "loggers": {
                "": {
                    "handlers": ["console", "file"],
                    "level": "INFO",
                    "propagate": False
                }
            }
        }
    
    def _get_docker_config(self) -> Dict[str, Any]:
        """Docker configuration optimized for container logging"""
        return {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "json": {
                    "()": structlog.stdlib.ProcessorFormatter,
                    "processor": structlog.processors.JSONRenderer(),
                }
            },
            "handlers": {
                "console": {
                    "class": "logging.StreamHandler",
                    "formatter": "json",
                    "level": "INFO"
                },
                "file": {
                    "class": "logging.handlers.RotatingFileHandler",
                    "filename": "/app/logs/docker-exai-mcp.log",
                    "maxBytes": 20971520,  # 20MB
                    "backupCount": 5,
                    "formatter": "json",
                    "level": "DEBUG"
                }
            },
            "loggers": {
                "": {
                    "handlers": ["console", "file"],
                    "level": "INFO",
                    "propagate": False
                }
            }
        }
    
    def _setup_logging(self):
        """Configure structlog and standard logging"""
        # Ensure logs directory exists
        log_dir = Path("logs")
        if self.environment == 'docker':
            log_dir = Path("/app/logs")
        log_dir.mkdir(parents=True, exist_ok=True)
        
        # Configure standard logging
        logging.config.dictConfig(self.config)
        
        # Configure structlog
        structlog.configure(
            processors=[
                structlog.stdlib.filter_by_level,
                structlog.stdlib.add_logger_name,
                structlog.stdlib.add_log_level,
                structlog.stdlib.PositionalArgumentsFormatter(),
                self._add_context,
                structlog.processors.TimeStamper(fmt="iso"),
                structlog.processors.StackInfoRenderer(),
                structlog.processors.format_exc_info,
                structlog.processors.UnicodeDecoder(),
                structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
            ],
            context_class=dict,
            logger_factory=structlog.stdlib.LoggerFactory(),
            wrapper_class=structlog.stdlib.BoundLogger,
            cache_logger_on_first_use=True,
        )
    
    def _add_context(self, logger, method_name: str, event_dict: Dict[str, Any]) -> Dict[str, Any]:
        """
        Add automatic context from context variables.
        
        This processor automatically enriches log entries with:
        - request_id: Current request identifier
        - session_id: Current session identifier
        - user_id: Current user identifier
        """
        if request_id_var.get():
            event_dict["request_id"] = request_id_var.get()
        if session_id_var.get():
            event_dict["session_id"] = session_id_var.get()
        if user_id_var.get():
            event_dict["user_id"] = user_id_var.get()
        
        # Add environment
        event_dict["environment"] = self.environment
        
        return event_dict
    
    def get_logger(self, name: str):
        """
        Get a properly configured logger.
        
        Args:
            name: Logger name (typically __name__)
            
        Returns:
            Configured structlog logger
        """
        return structlog.get_logger(name)
    
    def set_log_level(self, level: str):
        """
        Set global log level.
        
        Args:
            level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        """
        logging.getLogger().setLevel(getattr(logging, level.upper()))
    
    def configure_module_level(self, module: str, level: str):
        """
        Configure log level for specific module.
        
        Args:
            module: Module name
            level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        """
        logging.getLogger(module).setLevel(getattr(logging, level.upper()))


# Global singleton instance
_logging_manager: Optional[LoggingManager] = None


def get_logging_manager() -> LoggingManager:
    """
    Get or create the global logging manager instance.
    
    Returns:
        Global LoggingManager instance
    """
    global _logging_manager
    if _logging_manager is None:
        _logging_manager = LoggingManager()
    return _logging_manager


def get_logger(name: str):
    """
    Convenience function to get a logger.
    
    Args:
        name: Logger name (typically __name__)
        
    Returns:
        Configured structlog logger
    """
    return get_logging_manager().get_logger(name)

