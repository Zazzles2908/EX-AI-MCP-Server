"""
Test file for GLM file upload+chat workflow validation

This is a simple Python script to test the GLM file upload and chat functionality.
It contains basic functions to demonstrate code analysis capabilities.
"""

def calculate_sum(a: int, b: int) -> int:
    """Calculate the sum of two integers."""
    return a + b

def calculate_product(a: int, b: int) -> int:
    """Calculate the product of two integers."""
    return a * b

def greet(name: str) -> str:
    """Generate a greeting message."""
    return f"Hello, {name}!"

# Test data
test_numbers = [1, 2, 3, 4, 5]
test_result = sum(test_numbers)

if __name__ == "__main__":
    print(greet("World"))
    print(f"Sum: {calculate_sum(5, 3)}")
    print(f"Product: {calculate_product(5, 3)}")

