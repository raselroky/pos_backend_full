import re

class PhoneNumberValidator:
    def __init__(self, number):
        self.number = number
        self.bd_number_pattern = r'^(?:\+)?(?:88)?0[1-9]\d{9}$'
        
    def is_valid(self):
        if re.match(self.bd_number_pattern, self.number):
            return True
        return False
    
    
class EmailValidator:
    def __init__(self, email):
        self.email = email
        self.email_pattern = r'^[\w\.-]+@[a-zA-Z\d\.-]+\.[a-zA-Z]{2,}$'
        
    def is_valid(self):
        if re.match(self.email_pattern, self.email):
            return True
        return False