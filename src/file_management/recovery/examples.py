"""
Example usage of the Error Recovery Manager

This file demonstrates how to integrate and use the Error Recovery Manager
for robust file operations with comprehensive error handling and recovery.
"""

import tempfile
import logging
from pathlib import Path
from src.file_management.recovery import (
    ErrorRecoveryManager,
    ErrorType,
    recovery_operation
)


async def example_basic_usage():
    """Basic usage example of Error Recovery Manager"""
    
    logger.info("=== Basic Error Recovery Manager Usage ===")
    
    # Initialize with optional Supabase integration
    async with ErrorRecoveryManager(
        supabase_url="https://your-project.supabase.co",
        supabase_key="your-supabase-key"
    ) as recovery_manager:
        
        # Example operation that might fail
        async def risky_file_operation(file_path: str, data: str):
            # Simulate a risky operation that might fail
            await asyncio.sleep(0.1)  # Simulate I/O delay
            
            # Randomly fail to demonstrate recovery
            import random
            if random.random() < 0.3:  # 30% failure rate
                raise Exception("Simulated storage failure")
            
            # Write file if successful
            async with aiofiles.open(file_path, 'w') as f:
                await f.write(data)
            
            return f"Successfully wrote {len(data)} bytes to {file_path}"
        
        # Execute with full recovery mechanisms
        success, result, error = await recovery_manager.execute_with_recovery(
            risky_file_operation,
            "file_write_operation",
            "/tmp/example_file.txt",
            create_backup=True,
            "Hello, World! This is a test file."
        )
        
        if success:
            logger.info(f"✅ Operation succeeded: {result}")
        else:
            logger.info(f"❌ Operation failed: {error}")
        
        # Get recovery metrics
        metrics = await recovery_manager.get_recovery_metrics()
        logger.info(f"📊 Recovery metrics: {json.dumps(metrics, indent=2, default=str)}")


async def example_circuit_breaker():
    """Demonstrate circuit breaker pattern in action"""
    
    logger.info("\n=== Circuit Breaker Pattern Example ===")
    
    from src.file_management.recovery import CircuitBreakerConfig, CircuitBreaker
    
    # Configure circuit breaker with custom parameters
    config = CircuitBreakerConfig(
        failure_threshold=3,
        recovery_timeout=30.0
    )
    
    circuit_breaker = CircuitBreaker(config)
    
    # Simulate failing service
    async def failing_service():
        import random
        if random.random() < 0.7:  # 70% failure rate
            raise Exception("Service temporarily unavailable")
        return "Service response"
    
    # Use circuit breaker to protect the service
    for i in range(10):
        try:
            async with circuit_breaker.execute(failing_service):
                logger.info(f"✅ Attempt {i+1}: Service call succeeded")
        except Exception as e:
            logger.info(f"❌ Attempt {i+1}: Service call failed - {e}")
        
        await asyncio.sleep(0.5)  # Small delay between attempts


async def example_retry_mechanisms():
    """Demonstrate retry mechanisms with exponential backoff"""
    
    logger.info("\n=== Retry Mechanisms Example ===")
    
    async with ErrorRecoveryManager() as recovery_manager:
        
        # Configure custom retry behavior
        recovery_manager.retry_config.max_attempts = 5
        recovery_manager.retry_config.base_delay = 0.5
        recovery_manager.retry_config.backoff_factor = 2.0
        
        async def unreliable_operation():
            import random
            if random.random() < 0.6:  # 60% failure rate
                raise ConnectionError("Network connection failed")
            return "Operation successful"
        
        success, result, error = await recovery_manager.execute_with_recovery(
            unreliable_operation,
            "unreliable_network_operation"
        )
        
        logger.info(f"Retry result: {success}")
        logger.info(f"Result: {result}")
        logger.info(f"Error: {error}")


async def example_fallback_storage():
    """Demonstrate fallback storage mechanisms"""
    
    logger.info("\n=== Fallback Storage Example ===")
    
    async with ErrorRecoveryManager() as recovery_manager:
        
        async def storage_operation():
            # Simulate primary storage failure
            import random
            if random.random() < 0.5:
                raise Exception("Primary storage unavailable")
            
            # Return success message if primary storage works
            return "Data stored in primary storage"
        
        # Execute with automatic fallback to secondary storage
        success, result, error = await recovery_manager.execute_with_fallback(
            storage_operation
        )
        
        logger.info(f"Fallback storage result: {success}")
        logger.info(f"Storage used: {recovery_manager.fallback_storage.current_storage}")
        logger.info(f"Result: {result}")


async def example_rollback_operations():
    """Demonstrate file operation rollback capabilities"""
    
    logger.info("\n=== File Operation Rollback Example ===")
    
    async with ErrorRecoveryManager() as recovery_manager:
        
        # Create test file
        test_file = "/tmp/test_file.txt"
        await aiofiles.open(test_file, 'w').__aenter__().write("Original content")
        
        async def risky_file_update(file_path: str, new_content: str):
            # Simulate risky update that might corrupt file
            import random
            if random.random() < 0.4:
                raise Exception("File update failed")
            
            # Update file content
            async with aiofiles.open(file_path, 'w') as f:
                await f.write(new_content)
            
            return f"Updated file with {len(new_content)} bytes"
        
        # Execute with rollback capability
        success, result, error = await recovery_manager.execute_with_recovery(
            risky_file_update,
            "file_update_with_rollback",
            test_file,
            create_backup=True,
            "Updated content - this might fail"
        )
        
        logger.info(f"Update result: {success}")
        logger.info(f"Result: {result}")
        
        # Check if file content was preserved through rollback
        try:
            async with aiofiles.open(test_file, 'r') as f:
                content = await f.read()
            logger.info(f"Final file content: '{content}'")
        except Exception as e:
            logger.info(f"Failed to read file: {e}")


async def example_workflow_automation():
    """Demonstrate automated recovery workflows"""
    
    logger.info("\n=== Workflow Automation Example ===")
    
    async with ErrorRecoveryManager() as recovery_manager:
        
        # Define a workflow with multiple operations
        operations = [
            {
                "name": "prepare_data",
                "callable": lambda: asyncio.sleep(0.1) or "Data prepared",
                "args": [],
                "kwargs": {}
            },
            {
                "name": "process_data", 
                "callable": lambda: asyncio.sleep(0.1) or "Data processed",
                "args": [],
                "kwargs": {}
            },
            {
                "name": "save_results",
                "callable": lambda: asyncio.sleep(0.1) or "Results saved",
                "args": [],
                "kwargs": {}
            }
        ]
        
        # Create recovery workflow
        workflow_id = await recovery_manager.create_recovery_workflow(
            "data_processing_workflow",
            operations,
            rollback_on_failure=True
        )
        
        # Execute workflow
        success, errors = await recovery_manager.execute_recovery_workflow(workflow_id)
        
        logger.info(f"Workflow executed successfully: {success}")
        if errors:
            logger.info(f"Workflow errors: {errors}")


async def example_error_tracking():
    """Demonstrate Supabase error tracking integration"""
    
    logger.info("\n=== Error Tracking Example ===")
    
    # This would require actual Supabase credentials
    logger.info("Note: This example requires valid Supabase credentials")
    
    async with ErrorRecoveryManager(
        supabase_url="https://your-project.supabase.co",
        supabase_key="your-valid-supabase-key"
    ) as recovery_manager:
        
        # Generate some test errors
        for i in range(3):
            try:
                await recovery_manager.execute_with_recovery(
                    lambda: 1/0 if i < 2 else "success",
                    f"test_operation_{i}"
                )
            except:
                pass
        
        # Get error statistics
        metrics = await recovery_manager.get_recovery_metrics()
        logger.info(f"Error tracking metrics: {json.dumps(metrics.get('error_statistics', {}), indent=2, default=str)}")


async def example_decorator_usage():
    """Demonstrate decorator-based error recovery"""
    
    logger.info("\n=== Decorator Usage Example ===")
    
    async with ErrorRecoveryManager() as recovery_manager:
        
        # Apply decorator to function
        @recovery_operation(recovery_manager)
        async def decorated_operation(data: str):
            import random
            if random.random() < 0.3:
                raise Exception("Decorated operation failed")
            return f"Processed: {data}"
        
        # Execute decorated function
        try:
            result = await decorated_operation("test data")
            logger.info(f"Decorated function result: {result}")
        except Exception as e:
            logger.info(f"Decorated function failed: {e}")


async def main():
    """Run all examples"""
    logger.info("🚀 Error Recovery Manager Examples\n")
    
    try:
        await example_basic_usage()
        await example_circuit_breaker()
        await example_retry_mechanisms()
        await example_fallback_storage()
        await example_rollback_operations()
        await example_workflow_automation()
        await example_decorator_usage()
        await example_error_tracking()
        
        logger.info("\n✅ All examples completed successfully!")
        
    except Exception as e:
        logger.info(f"\n❌ Example failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    # Import required modules
    import aiofiles
    import json
    
    asyncio.run(main())