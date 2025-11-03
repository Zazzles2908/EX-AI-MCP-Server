"""
Sample code for testing workflow tools
Simple function with potential improvements
"""

def calculate_total(items):
    """Calculate total price of items"""
    total = 0
    for item in items:
        if item['price'] > 0:
            total = total + item['price']
    return total

def process_user_data(user_input):
    """Process user data without validation"""
    # No input validation
    result = eval(user_input)  # Security issue
    return result

class UserManager:
    def __init__(self):
        self.users = []
    
    def add_user(self, name, email):
        # No duplicate checking
        self.users.append({'name': name, 'email': email})
        return True

