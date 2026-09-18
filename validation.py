import re
from datetime import datetime


def validate_required(value, field_name):
    value = value.strip()

    if value == "":
        print(f"❌ {field_name} cannot be empty!")
        return False

    return True


def validate_name(name):
    name = name.strip()

    if name == "":
        print("❌ Name cannot be empty!")
        return False

    if len(name) < 3:
        print("❌ Name must contain at least 3 characters!")
        return False

    if not all(ch.isalpha() or ch.isspace() for ch in name):
        print("❌ Name can contain only letters and spaces!")
        return False

    return True


def validate_email(email):
    email = email.strip()

    pattern = r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$"

    if not re.match(pattern, email):
        print("❌ Please enter a valid email address!")
        return False

    return True


def validate_phone(phone):
    phone = phone.strip()

    if not phone.isdigit():
        print("❌ Phone number must contain only digits!")
        return False

    if len(phone) != 10:
        print("❌ Phone number must contain exactly 10 digits!")
        return False

    return True


def validate_salary(salary):
    try:
        salary = float(salary)

        if salary <= 0:
            print("❌ Salary must be greater than 0!")
            return False

        return True

    except ValueError:
        print("❌ Salary must be a valid number!")
        return False


def validate_date(date_string):
    try:
        datetime.strptime(date_string, "%Y-%m-%d")
        return True

    except ValueError:
        print("❌ Invalid date! Use YYYY-MM-DD format.")
        return False

if __name__ == "__main__":
    print(validate_name("Rahul Patel"))
    print(validate_email("rahul@gmail.com"))
    print(validate_phone("9876543210"))
    print(validate_salary("45000"))
    print(validate_date("2026-08-13"))    