"""
Sample Python code for testing EXAI file upload and extraction capabilities.
This file contains imports, a class, functions, and comments for validation.
"""

import os
import json
from typing import List, Dict, Optional


class DataProcessor:
    """Process and validate data from various sources."""
    
    def __init__(self, config_path: str):
        self.config_path = config_path
        self.data = []
    
    def load_config(self) -> Dict:
        """Load configuration from JSON file."""
        with open(self.config_path, 'r') as f:
            return json.load(f)
    
    def process_data(self, items: List[str]) -> List[str]:
        """Process a list of items and return cleaned results."""
        return [item.strip().lower() for item in items if item]
    
    def validate_data(self, data: Dict) -> bool:
        """Validate data structure and required fields."""
        required_fields = ['name', 'version', 'providers']
        return all(field in data for field in required_fields)


def calculate_sum(a: int, b: int) -> int:
    """Calculate sum of two numbers."""
    return a + b


def main():
    """Main entry point for testing."""
    processor = DataProcessor('config.json')
    result = calculate_sum(5, 3)
    print(f'Result: {result}')


if __name__ == '__main__':
    main()

