import uuid
import random
from django.db import models

def generate_invoice_no():
    prefix = "INV"
    random_number = random.randint(1000, 9999)
    random_last=random.randint(100,999)
    random_font=random.randint(10,99)
    s='abcdefghijklmnopqrstuvwxyz'
    ss='ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    random_string1 = ''.join(random.choices(s, k=1))
    random_string2 = ''.join(random.choices(ss, k=1))
    x=random_string1+random_string2
    return f"{prefix}{x}{random_font}{random_number}{random_last}"


def generate_return_no():
    prefix = "RET"
    random_number = random.randint(1000, 9999)
    random_last=random.randint(100,999)
    random_font=random.randint(10,99)
    s='abcdefghijklmnopqrstuvwxyz'
    ss='ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    random_string1 = ''.join(random.choices(s, k=1))
    random_string2 = ''.join(random.choices(ss, k=1))
    x=random_string1+random_string2
    return f"{prefix}{x}{random_font}{random_number}{random_last}"