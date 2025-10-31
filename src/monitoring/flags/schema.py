"""
Feature Flag Schema and Definitions

Defines all monitoring system feature flags with validation rules and defaults.
"""

from dataclasses import dataclass
from typing import Any, Dict, Optional, Type, Union
from enum import Enum


class FlagType(Enum):
    """Supported flag data types"""
    BOOL = 'bool'
    STRING = 'string'
    INT = 'int'
    FLOAT = 'float'


@dataclass
class FlagDefinition:
    """Definition of a single feature flag"""
    
    name: str
    flag_type: FlagType
    default: Any
    description: str
    env_var: str
    validator: Optional[callable] = None
    
    def validate(self, value: Any) -> bool:
        """Validate flag value"""
        if value is None:
            return True
        
        # Type check
        type_map = {
            FlagType.BOOL: bool,
            FlagType.STRING: str,
            FlagType.INT: int,
            FlagType.FLOAT: float,
        }
        
        if not isinstance(value, type_map[self.flag_type]):
            return False
        
        # Custom validator
        if self.validator:
            return self.validator(value)
        
        return True


class FlagSchema:
    """Schema for all monitoring system feature flags"""
    
    # Adapter configuration flags
    MONITORING_USE_ADAPTER = FlagDefinition(
        name='MONITORING_USE_ADAPTER',
        flag_type=FlagType.BOOL,
        default=True,
        description='Enable monitoring adapter',
        env_var='MONITORING_USE_ADAPTER',
    )
    
    MONITORING_ADAPTER_TYPE = FlagDefinition(
        name='MONITORING_ADAPTER_TYPE',
        flag_type=FlagType.STRING,
        default='realtime',
        description='Monitoring adapter type: websocket, realtime, or dual',
        env_var='MONITORING_ADAPTER_TYPE',
        validator=lambda x: x in ['websocket', 'realtime', 'dual'],
    )
    
    MONITORING_DUAL_MODE = FlagDefinition(
        name='MONITORING_DUAL_MODE',
        flag_type=FlagType.BOOL,
        default=False,
        description='Run both WebSocket and Realtime adapters in parallel',
        env_var='MONITORING_DUAL_MODE',
    )
    
    # Validation flags
    MONITORING_ENABLE_VALIDATION = FlagDefinition(
        name='MONITORING_ENABLE_VALIDATION',
        flag_type=FlagType.BOOL,
        default=True,
        description='Enable event validation',
        env_var='MONITORING_ENABLE_VALIDATION',
    )
    
    MONITORING_VALIDATION_STRICT = FlagDefinition(
        name='MONITORING_VALIDATION_STRICT',
        flag_type=FlagType.BOOL,
        default=False,
        description='Fail on validation errors (block broadcasts)',
        env_var='MONITORING_VALIDATION_STRICT',
    )
    
    # Metrics flags
    MONITORING_METRICS_FLUSH_INTERVAL = FlagDefinition(
        name='MONITORING_METRICS_FLUSH_INTERVAL',
        flag_type=FlagType.INT,
        default=300,
        description='Metrics flush interval in seconds',
        env_var='MONITORING_METRICS_FLUSH_INTERVAL',
        validator=lambda x: x > 0,
    )
    
    MONITORING_METRICS_PERSISTENCE = FlagDefinition(
        name='MONITORING_METRICS_PERSISTENCE',
        flag_type=FlagType.BOOL,
        default=True,
        description='Enable metrics persistence to database',
        env_var='MONITORING_METRICS_PERSISTENCE',
    )
    
    # Performance flags
    MONITORING_BATCH_SIZE = FlagDefinition(
        name='MONITORING_BATCH_SIZE',
        flag_type=FlagType.INT,
        default=100,
        description='Batch size for bulk operations',
        env_var='MONITORING_BATCH_SIZE',
        validator=lambda x: x > 0,
    )
    
    MONITORING_TIMEOUT_MS = FlagDefinition(
        name='MONITORING_TIMEOUT_MS',
        flag_type=FlagType.INT,
        default=5000,
        description='Operation timeout in milliseconds',
        env_var='MONITORING_TIMEOUT_MS',
        validator=lambda x: x > 0,
    )
    
    @classmethod
    def get_all_flags(cls) -> Dict[str, FlagDefinition]:
        """Get all flag definitions"""
        return {
            name: getattr(cls, name)
            for name in dir(cls)
            if not name.startswith('_') and isinstance(getattr(cls, name), FlagDefinition)
        }
    
    @classmethod
    def get_flag(cls, name: str) -> Optional[FlagDefinition]:
        """Get flag definition by name"""
        return getattr(cls, name, None)

