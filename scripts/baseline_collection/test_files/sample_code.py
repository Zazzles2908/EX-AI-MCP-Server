#!/usr/bin/env python3
"""
Sample Python code file for testing file upload functionality.

This file demonstrates basic Python code structure.
"""


def hello_world():
    """Print a greeting message."""
    print("Hello, World!")


def add_numbers(a: int, b: int) -> int:
    """
    Add two numbers together.
    
    Args:
        a: First number
        b: Second number
        
    Returns:
        Sum of a and b
    """
    return a + b


class Calculator:
    """Simple calculator class."""
    
    def __init__(self):
        """Initialize calculator."""
        self.result = 0
    
    def add(self, value: int) -> int:
        """Add value to result."""
        self.result += value
        return self.result
    
    def subtract(self, value: int) -> int:
        """Subtract value from result."""
        self.result -= value
        return self.result
    
    def reset(self):
        """Reset result to zero."""
        self.result = 0


if __name__ == "__main__":
    hello_world()
    print(f"2 + 3 = {add_numbers(2, 3)}")
    
    calc = Calculator()
    calc.add(10)
    calc.subtract(3)
    print(f"Calculator result: {calc.result}")

