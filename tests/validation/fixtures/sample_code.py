"""
Sample Python code for testing workflow tools.

This file contains intentional issues for testing:
- Code review opportunities
- Refactoring suggestions
- Security concerns
- Performance improvements
"""

def calculate_sum(numbers):
    """Calculate sum of numbers in a list."""
    # Inefficient: using manual loop instead of built-in sum()
    total = 0
    for num in numbers:
        total = total + num
    return total


def divide_numbers(a, b):
    """Divide two numbers."""
    # Security issue: no validation of inputs
    # Bug: no check for division by zero
    return a / b


def process_user_input(user_data):
    """Process user input."""
    # Security issue: potential SQL injection
    query = f"SELECT * FROM users WHERE name = '{user_data}'"
    return query


def find_max(numbers):
    """Find maximum number in list."""
    # Inefficient: manual comparison instead of built-in max()
    if len(numbers) == 0:
        return None
    
    max_num = numbers[0]
    for num in numbers:
        if num > max_num:
            max_num = num
    return max_num


class DataProcessor:
    """Process data with various methods."""
    
    def __init__(self):
        self.data = []
    
    def add_item(self, item):
        """Add item to data list."""
        # Missing validation
        self.data.append(item)
    
    def get_average(self):
        """Calculate average of data."""
        # Bug: no check for empty list
        return sum(self.data) / len(self.data)
    
    def save_to_file(self, filename):
        """Save data to file."""
        # Security issue: no path validation
        # Bug: no error handling
        with open(filename, 'w') as f:
            f.write(str(self.data))


def main():
    """Main function."""
    numbers = [1, 2, 3, 4, 5]
    
    # Test sum
    result = calculate_sum(numbers)
    print(f"Sum: {result}")
    
    # Test division (potential error)
    div_result = divide_numbers(10, 2)
    print(f"Division: {div_result}")
    
    # Test max
    max_num = find_max(numbers)
    print(f"Max: {max_num}")
    
    # Test data processor
    processor = DataProcessor()
    for num in numbers:
        processor.add_item(num)
    
    avg = processor.get_average()
    print(f"Average: {avg}")


if __name__ == "__main__":
    main()

