from database import create_connection


def generate_employee_code():
    connection = create_connection()

    if connection is None:
        return None

    try:
        cursor = connection.cursor()

        query = """
            SELECT employee_code
            FROM employees
            ORDER BY employee_id DESC
            LIMIT 1
        """

        cursor.execute(query)

        result = cursor.fetchone()

        cursor.close()
        connection.close()

        if result is None:
            return "EMP1001"

        last_code = result[0]

        number = int(last_code.replace("EMP", ""))

        new_number = number + 1

        return f"EMP{new_number}"

    except Exception as e:
        print(f"❌ Error generating employee code: {e}")

        if connection.is_connected():
            connection.close()

        return None



from validation import (
    validate_name,
    validate_email,
    validate_phone,
    validate_salary,
    validate_date
)


def get_department_id():
    connection = create_connection()

    if connection is None:
        return None

    try:
        cursor = connection.cursor(dictionary=True)

        cursor.execute("""
            SELECT department_id, department_name
            FROM departments
            ORDER BY department_id
        """)

        departments = cursor.fetchall()

        cursor.close()
        connection.close()

        if not departments:
            print("❌ No departments found!")
            return None

        print("\nAvailable Departments")
        print("-" * 35)

        for department in departments:
            print(
                f"{department['department_id']}. "
                f"{department['department_name']}"
            )

        while True:
            choice = input("\nEnter Department ID: ").strip()

            if not choice.isdigit():
                print("❌ Please enter a valid department ID!")
                continue

            department_id = int(choice)

            for department in departments:
                if department["department_id"] == department_id:
                    return department_id

            print("❌ Invalid department ID!")

    except Exception as e:
        print(f"❌ Error loading departments: {e}")
        return None


def add_employee():

    print("\n")
    print("=" * 50)
    print("              ADD NEW EMPLOYEE")
    print("=" * 50)

    # Employee Name
    while True:
        name = input("Enter Employee Name: ").strip()

        if validate_name(name):
            break

    # Email
    while True:
        email = input("Enter Email: ").strip()

        if validate_email(email):
            break

    # Phone
    while True:
        phone = input("Enter Phone Number: ").strip()

        if validate_phone(phone):
            break

    # Department
    department_id = get_department_id()

    if department_id is None:
        return

    # Designation
    while True:
        designation = input("Enter Designation: ").strip()

        if designation == "":
            print("❌ Designation cannot be empty!")
            continue

        if len(designation) < 2:
            print("❌ Designation is too short!")
            continue

        break

    # Salary
    while True:
        salary = input("Enter Salary: ").strip()

        if validate_salary(salary):
            salary = float(salary)
            break

    # Date of Birth
    while True:
        date_of_birth = input(
            "Enter Date of Birth (YYYY-MM-DD): "
        ).strip()

        if validate_date(date_of_birth):
            break

    # Joining Date
    while True:
        joining_date = input(
            "Enter Joining Date (YYYY-MM-DD): "
        ).strip()

        if validate_date(joining_date):
            break

    # Generate Employee Code
    employee_code = generate_employee_code()

    if employee_code is None:
        return

    connection = create_connection()

    if connection is None:
        return

    try:
        cursor = connection.cursor()

        # Check duplicate email
        cursor.execute(
            "SELECT employee_id FROM employees WHERE email = %s",
            (email,)
        )

        if cursor.fetchone():
            print("❌ This email is already registered!")
            cursor.close()
            connection.close()
            return

        # Check duplicate phone
        cursor.execute(
            "SELECT employee_id FROM employees WHERE phone = %s",
            (phone,)
        )

        if cursor.fetchone():
            print("❌ This phone number is already registered!")
            cursor.close()
            connection.close()
            return

        # Insert employee
        query = """
            INSERT INTO employees
            (
                employee_code,
                full_name,
                email,
                phone,
                department_id,
                designation,
                salary,
                date_of_birth,
                joining_date
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """

        values = (
            employee_code,
            name,
            email,
            phone,
            department_id,
            designation,
            salary,
            date_of_birth,
            joining_date
        )

        cursor.execute(query, values)

        employee_id = cursor.lastrowid

        # Create leave balance
        cursor.execute("""
            INSERT INTO leave_balances
            (employee_id)
            VALUES (%s)
        """, (employee_id,))

        # Create employee login
        username = employee_code
        password = f"{employee_code}@123"

        cursor.execute("""
            INSERT INTO users
            (employee_id, username, password, role)
            VALUES (%s, %s, %s, 'Employee')
        """, (
            employee_id,
            username,
            password
        ))

        connection.commit()

        print("\n" + "=" * 50)
        print("       ✅ EMPLOYEE CREATED SUCCESSFULLY")
        print("=" * 50)

        print(f"Employee ID    : {employee_code}")
        print(f"Name           : {name}")
        print(f"Email          : {email}")
        print(f"Phone          : {phone}")
        print(f"Designation    : {designation}")
        print(f"Salary         : ₹{salary:.2f}")

        print("\n🔐 Employee Login")
        print(f"Username       : {username}")
        print(f"Temporary Password : {password}")

        print("=" * 50)

        cursor.close()
        connection.close()

    except Exception as e:
        connection.rollback()
        print(f"❌ Failed to add employee: {e}")

        cursor.close()
        connection.close()    


def view_all_employees():

    connection = create_connection()

    if connection is None:
        return

    try:
        cursor = connection.cursor(dictionary=True)

        query = """
            SELECT
                e.employee_code,
                e.full_name,
                d.department_name,
                e.designation,
                e.salary,
                e.status
            FROM employees e
            INNER JOIN departments d
                ON e.department_id = d.department_id
            ORDER BY e.employee_id
        """

        cursor.execute(query)

        employees = cursor.fetchall()

        cursor.close()
        connection.close()

        if not employees:
            print("\n❌ No employees found!")
            return

        print("\n")
        print("=" * 95)
        print(" " * 32 + "ALL EMPLOYEES")
        print("=" * 95)

        print(
            f"{'ID':<10}"
            f"{'NAME':<22}"
            f"{'DEPARTMENT':<18}"
            f"{'DESIGNATION':<22}"
            f"{'SALARY':<12}"
            f"{'STATUS':<10}"
        )

        print("-" * 95)

        for employee in employees:

            print(
                f"{employee['employee_code']:<10}"
                f"{employee['full_name']:<22}"
                f"{employee['department_name']:<18}"
                f"{employee['designation']:<22}"
                f"₹{employee['salary']:<11.2f}"
                f"{employee['status']:<10}"
            )

        print("=" * 95)

    except Exception as e:
        print(f"❌ Error displaying employees: {e}")

        if connection.is_connected():
            connection.close()        



def search_employee():
    print("\n")
    print("=" * 50)
    print("              SEARCH EMPLOYEE")
    print("=" * 50)

    print("1. Search by Employee ID")
    print("2. Search by Name")
    print("3. Search by Email")
    print("4. Search by Phone")
    print("5. Search by Department")
    print("6. Back")

    choice = input("\nEnter your choice: ").strip()

    if choice == "6":
        return

    search_value = input("Enter search value: ").strip()

    if search_value == "":
        print("❌ Search value cannot be empty!")
        return

    connection = create_connection()

    if connection is None:
        return

    try:
        cursor = connection.cursor(dictionary=True)

        base_query = """
            SELECT
                e.employee_code,
                e.full_name,
                e.email,
                e.phone,
                d.department_name,
                e.designation,
                e.salary,
                e.date_of_birth,
                e.joining_date,
                e.status
            FROM employees e
            INNER JOIN departments d
                ON e.department_id = d.department_id
        """

        if choice == "1":
            query = base_query + """
                WHERE e.employee_code = %s
            """
            cursor.execute(query, (search_value,))

        elif choice == "2":
            query = base_query + """
                WHERE e.full_name LIKE %s
            """
            cursor.execute(query, (f"%{search_value}%",))

        elif choice == "3":
            query = base_query + """
                WHERE e.email = %s
            """
            cursor.execute(query, (search_value,))

        elif choice == "4":
            query = base_query + """
                WHERE e.phone = %s
            """
            cursor.execute(query, (search_value,))

        elif choice == "5":
            query = base_query + """
                WHERE d.department_name LIKE %s
            """
            cursor.execute(query, (f"%{search_value}%",))

        else:
            print("❌ Invalid choice!")
            cursor.close()
            connection.close()
            return

        employees = cursor.fetchall()

        cursor.close()
        connection.close()

        if not employees:
            print("\n❌ No employee found!")
            return

        print("\n")
        print("=" * 55)
        print("              SEARCH RESULTS")
        print("=" * 55)

        for employee in employees:

            print(f"""
Employee ID    : {employee['employee_code']}
Full Name      : {employee['full_name']}
Email          : {employee['email']}
Phone          : {employee['phone']}
Department     : {employee['department_name']}
Designation    : {employee['designation']}
Salary         : ₹{employee['salary']:.2f}
Date of Birth  : {employee['date_of_birth']}
Joining Date   : {employee['joining_date']}
Status         : {employee['status']}
""")

            print("-" * 55)

    except Exception as e:
        print(f"❌ Search error: {e}")

        if connection.is_connected():
            connection.close()




def update_employee():

    print("\n")
    print("=" * 50)
    print("              UPDATE EMPLOYEE")
    print("=" * 50)

    employee_code = input("Enter Employee ID: ").strip().upper()

    if employee_code == "":
        print("❌ Employee ID cannot be empty!")
        return

    connection = create_connection()

    if connection is None:
        return

    try:
        cursor = connection.cursor(dictionary=True)

        # Find employee
        cursor.execute("""
            SELECT
                e.*,
                d.department_name
            FROM employees e
            INNER JOIN departments d
                ON e.department_id = d.department_id
            WHERE e.employee_code = %s
        """, (employee_code,))

        employee = cursor.fetchone()

        if employee is None:
            print("❌ Employee not found!")
            cursor.close()
            connection.close()
            return

        # Display current details
        print("\nCurrent Employee Details")
        print("-" * 50)
        print(f"Employee ID : {employee['employee_code']}")
        print(f"Name        : {employee['full_name']}")
        print(f"Email       : {employee['email']}")
        print(f"Phone       : {employee['phone']}")
        print(f"Department  : {employee['department_name']}")
        print(f"Designation : {employee['designation']}")
        print(f"Salary      : ₹{employee['salary']:.2f}")
        print(f"DOB         : {employee['date_of_birth']}")
        print(f"Joining     : {employee['joining_date']}")
        print(f"Status      : {employee['status']}")
        print("-" * 50)

        print("\nWhat do you want to update?")
        print("1. Name")
        print("2. Email")
        print("3. Phone")
        print("4. Department")
        print("5. Designation")
        print("6. Salary")
        print("7. Date of Birth")
        print("8. Joining Date")
        print("9. Status")
        print("10. Back")

        choice = input("\nEnter your choice: ").strip()

        if choice == "10":
            cursor.close()
            connection.close()
            return

        # ---------------- NAME ----------------
        if choice == "1":

            while True:
                new_value = input("Enter New Name: ").strip()

                if validate_name(new_value):
                    break

            query = """
                UPDATE employees
                SET full_name = %s
                WHERE employee_id = %s
            """

            cursor.execute(query, (new_value, employee["employee_id"]))

        # ---------------- EMAIL ----------------
        elif choice == "2":

            while True:
                new_value = input("Enter New Email: ").strip()

                if not validate_email(new_value):
                    continue

                cursor.execute("""
                    SELECT employee_id
                    FROM employees
                    WHERE email = %s
                    AND employee_id != %s
                """, (new_value, employee["employee_id"]))

                if cursor.fetchone():
                    print("❌ This email is already used by another employee!")
                    continue

                break

            cursor.execute("""
                UPDATE employees
                SET email = %s
                WHERE employee_id = %s
            """, (new_value, employee["employee_id"]))

        # ---------------- PHONE ----------------
        elif choice == "3":

            while True:
                new_value = input("Enter New Phone: ").strip()

                if not validate_phone(new_value):
                    continue

                cursor.execute("""
                    SELECT employee_id
                    FROM employees
                    WHERE phone = %s
                    AND employee_id != %s
                """, (new_value, employee["employee_id"]))

                if cursor.fetchone():
                    print("❌ This phone number is already used!")
                    continue

                break

            cursor.execute("""
                UPDATE employees
                SET phone = %s
                WHERE employee_id = %s
            """, (new_value, employee["employee_id"]))

        # ---------------- DEPARTMENT ----------------
        elif choice == "4":

            cursor.close()
            connection.close()

            new_department = get_department_id()

            if new_department is None:
                return

            connection = create_connection()

            if connection is None:
                return

            cursor = connection.cursor()

            cursor.execute("""
                UPDATE employees
                SET department_id = %s
                WHERE employee_id = %s
            """, (new_department, employee["employee_id"]))

        # ---------------- DESIGNATION ----------------
        elif choice == "5":

            while True:
                new_value = input("Enter New Designation: ").strip()

                if new_value == "":
                    print("❌ Designation cannot be empty!")
                    continue

                if len(new_value) < 2:
                    print("❌ Designation is too short!")
                    continue

                break

            cursor.execute("""
                UPDATE employees
                SET designation = %s
                WHERE employee_id = %s
            """, (new_value, employee["employee_id"]))

        # ---------------- SALARY ----------------
        elif choice == "6":

            while True:
                new_value = input("Enter New Salary: ").strip()

                if validate_salary(new_value):
                    new_value = float(new_value)
                    break

            cursor.execute("""
                UPDATE employees
                SET salary = %s
                WHERE employee_id = %s
            """, (new_value, employee["employee_id"]))

        # ---------------- DOB ----------------
        elif choice == "7":

            while True:
                new_value = input(
                    "Enter New Date of Birth (YYYY-MM-DD): "
                ).strip()

                if validate_date(new_value):
                    break

            cursor.execute("""
                UPDATE employees
                SET date_of_birth = %s
                WHERE employee_id = %s
            """, (new_value, employee["employee_id"]))

        # ---------------- JOINING DATE ----------------
        elif choice == "8":

            while True:
                new_value = input(
                    "Enter New Joining Date (YYYY-MM-DD): "
                ).strip()

                if validate_date(new_value):
                    break

            cursor.execute("""
                UPDATE employees
                SET joining_date = %s
                WHERE employee_id = %s
            """, (new_value, employee["employee_id"]))

        # ---------------- STATUS ----------------
        elif choice == "9":

            print("\nAvailable Status")
            print("1. Active")
            print("2. Inactive")
            print("3. On Leave")

            status_choice = input("Enter choice: ").strip()

            status_map = {
                "1": "Active",
                "2": "Inactive",
                "3": "On Leave"
            }

            if status_choice not in status_map:
                print("❌ Invalid status choice!")
                cursor.close()
                connection.close()
                return

            new_value = status_map[status_choice]

            cursor.execute("""
                UPDATE employees
                SET status = %s
                WHERE employee_id = %s
            """, (new_value, employee["employee_id"]))

        else:
            print("❌ Invalid choice!")
            cursor.close()
            connection.close()
            return

        connection.commit()

        print("\n✅ Employee updated successfully!")

        cursor.close()
        connection.close()

    except Exception as e:

        connection.rollback()

        print(f"❌ Error updating employee: {e}")

        if connection.is_connected():
            connection.close()        




def delete_employee():

    print("\n")
    print("=" * 50)
    print("              DELETE EMPLOYEE")
    print("=" * 50)

    employee_code = input("Enter Employee ID: ").strip().upper()

    if employee_code == "":
        print("❌ Employee ID cannot be empty!")
        return

    connection = create_connection()

    if connection is None:
        return

    try:
        cursor = connection.cursor(dictionary=True)

        # Find employee
        cursor.execute("""
            SELECT
                e.employee_id,
                e.employee_code,
                e.full_name,
                e.email,
                e.phone,
                d.department_name,
                e.designation,
                e.salary,
                e.status
            FROM employees e
            INNER JOIN departments d
                ON e.department_id = d.department_id
            WHERE e.employee_code = %s
        """, (employee_code,))

        employee = cursor.fetchone()

        if employee is None:
            print("❌ Employee not found!")
            cursor.close()
            connection.close()
            return

        # Display employee
        print("\nEmployee Information")
        print("-" * 50)

        print(f"Employee ID : {employee['employee_code']}")
        print(f"Name        : {employee['full_name']}")
        print(f"Email       : {employee['email']}")
        print(f"Phone       : {employee['phone']}")
        print(f"Department  : {employee['department_name']}")
        print(f"Designation : {employee['designation']}")
        print(f"Salary      : ₹{employee['salary']:.2f}")
        print(f"Status      : {employee['status']}")

        print("-" * 50)

        print("\n⚠️ WARNING!")
        print("Deleting this employee will also remove")
        print("their related login, leave balance,")
        print("leave requests, attendance records,")
        print("and project assignments.")

        confirmation = input(
            "\nAre you sure you want to delete this employee? (Y/N): "
        ).strip().upper()

        if confirmation != "Y":
            print("\n❌ Deletion cancelled.")

            cursor.close()
            connection.close()
            return

        # Delete employee
        cursor.execute("""
            DELETE FROM employees
            WHERE employee_id = %s
        """, (employee["employee_id"],))

        connection.commit()

        print("\n" + "=" * 50)
        print("      ✅ EMPLOYEE DELETED SUCCESSFULLY")
        print("=" * 50)

        print(f"Employee ID : {employee['employee_code']}")
        print(f"Name        : {employee['full_name']}")
        print("=" * 50)

        cursor.close()
        connection.close()

    except Exception as e:

        connection.rollback()

        print(f"❌ Error deleting employee: {e}")

        if connection.is_connected():
            connection.close()




def view_employee_details():

    print("\n")
    print("=" * 55)
    print("              EMPLOYEE PROFILE")
    print("=" * 55)

    employee_code = input("Enter Employee ID: ").strip().upper()

    if employee_code == "":
        print("❌ Employee ID cannot be empty!")
        return

    connection = create_connection()

    if connection is None:
        return

    try:
        cursor = connection.cursor(dictionary=True)

        query = """
            SELECT
                e.employee_id,
                e.employee_code,
                e.full_name,
                e.email,
                e.phone,
                d.department_name,
                e.designation,
                e.salary,
                e.date_of_birth,
                e.joining_date,
                e.status
            FROM employees e
            INNER JOIN departments d
                ON e.department_id = d.department_id
            WHERE e.employee_code = %s
        """

        cursor.execute(query, (employee_code,))

        employee = cursor.fetchone()

        if employee is None:
            print("❌ Employee not found!")
            cursor.close()
            connection.close()
            return

        print("\n")
        print("╔" + "═" * 53 + "╗")
        print("║" + " EMPLOYEE PROFILE ".center(53) + "║")
        print("╠" + "═" * 53 + "╣")

        print(
            f"║ Employee ID    : "
            f"{employee['employee_code']:<34}║"
        )

        print(
            f"║ Name           : "
            f"{employee['full_name']:<34}║"
        )

        print(
            f"║ Email          : "
            f"{employee['email']:<34}║"
        )

        print(
            f"║ Phone          : "
            f"{employee['phone']:<34}║"
        )

        print(
            f"║ Department     : "
            f"{employee['department_name']:<34}║"
        )

        print(
            f"║ Designation    : "
            f"{employee['designation']:<34}║"
        )

        print(
            f"║ Salary         : "
            f"₹{employee['salary']:<33.2f}║"
        )

        print(
            f"║ Date of Birth  : "
            f"{str(employee['date_of_birth']):<34}║"
        )

        print(
            f"║ Joining Date   : "
            f"{str(employee['joining_date']):<34}║"
        )

        print(
            f"║ Status         : "
            f"{employee['status']:<34}║"
        )

        print("╚" + "═" * 53 + "╝")

        cursor.close()
        connection.close()

    except Exception as e:

        print(f"❌ Error loading employee details: {e}")

        if connection.is_connected():
            connection.close()                            