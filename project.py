from datetime import datetime
from database import create_connection


# ============================================================
# HELPER - GET EMPLOYEE BY CODE
# ============================================================

def get_employee_by_code(employee_code):

    connection = create_connection()

    if connection is None:
        return None

    try:

        cursor = connection.cursor(dictionary=True)

        cursor.execute("""
            SELECT
                e.employee_id,
                e.employee_code,
                e.full_name,
                e.email,
                e.designation,
                e.status,
                d.department_name
            FROM employees e
            INNER JOIN departments d
                ON e.department_id = d.department_id
            WHERE e.employee_code = %s
        """, (employee_code,))

        employee = cursor.fetchone()

        cursor.close()
        connection.close()

        return employee

    except Exception as e:

        print(f"\n❌ Error finding employee: {e}")

        if connection.is_connected():
            connection.close()

        return None


# ============================================================
# HELPER - GET PROJECT BY CODE
# ============================================================

def get_project_by_code(project_code):

    connection = create_connection()

    if connection is None:
        return None

    try:

        cursor = connection.cursor(dictionary=True)

        cursor.execute("""
            SELECT
                project_id,
                project_code,
                project_name,
                client_name,
                description,
                start_date,
                end_date,
                status,
                created_at
            FROM projects
            WHERE project_code = %s
        """, (project_code,))

        project = cursor.fetchone()

        cursor.close()
        connection.close()

        return project

    except Exception as e:

        print(f"\n❌ Error finding project: {e}")

        if connection.is_connected():
            connection.close()

        return None


# ============================================================
# HELPER - GENERATE PROJECT CODE
# ============================================================

def generate_project_code():

    connection = create_connection()

    if connection is None:
        return None

    try:

        cursor = connection.cursor()

        cursor.execute("""
            SELECT project_code
            FROM projects
            ORDER BY project_id DESC
            LIMIT 1
        """)

        result = cursor.fetchone()

        if result is None:
            project_number = 1001

        else:

            last_code = result[0]

            try:
                project_number = int(last_code.replace("PROJ", "")) + 1

            except ValueError:
                project_number = 1001

        project_code = f"PROJ{project_number}"

        cursor.close()
        connection.close()

        return project_code

    except Exception as e:

        print(f"\n❌ Error generating project code: {e}")

        if connection.is_connected():
            connection.close()

        return None


# ============================================================
# ADMIN - ADD PROJECT
# ============================================================

def add_project():

    connection = create_connection()

    if connection is None:
        return

    try:

        cursor = connection.cursor(dictionary=True)

        print("\n")
        print("=" * 70)
        print("                       ADD PROJECT")
        print("=" * 70)

        project_code = generate_project_code()

        if project_code is None:

            cursor.close()
            connection.close()
            return

        print(f"\nGenerated Project Code: {project_code}")

        # --------------------------------------------------
        # PROJECT NAME
        # --------------------------------------------------

        while True:

            project_name = input(
                "Enter Project Name: "
            ).strip()

            if project_name == "":
                print("❌ Project name cannot be empty!")
                continue

            if len(project_name) > 150:
                print("❌ Project name cannot exceed 150 characters!")
                continue

            break

        # --------------------------------------------------
        # CLIENT NAME
        # --------------------------------------------------

        while True:

            client_name = input(
                "Enter Client Name: "
            ).strip()

            if len(client_name) > 150:
                print("❌ Client name cannot exceed 150 characters!")
                continue

            break

        # --------------------------------------------------
        # DESCRIPTION
        # --------------------------------------------------

        description = input(
            "Enter Project Description: "
        ).strip()

        # --------------------------------------------------
        # START DATE
        # --------------------------------------------------

        while True:

            start_date_input = input(
                "Enter Start Date (YYYY-MM-DD): "
            ).strip()

            try:

                start_date = datetime.strptime(
                    start_date_input,
                    "%Y-%m-%d"
                ).date()

                break

            except ValueError:

                print(
                    "❌ Invalid date format! Use YYYY-MM-DD."
                )

        # --------------------------------------------------
        # END DATE
        # --------------------------------------------------

        while True:

            end_date_input = input(
                "Enter End Date (YYYY-MM-DD) or press Enter: "
            ).strip()

            if end_date_input == "":
                end_date = None
                break

            try:

                end_date = datetime.strptime(
                    end_date_input,
                    "%Y-%m-%d"
                ).date()

                if end_date < start_date:

                    print(
                        "❌ End date cannot be before start date!"
                    )
                    continue

                break

            except ValueError:

                print(
                    "❌ Invalid date format! Use YYYY-MM-DD."
                )

        # --------------------------------------------------
        # STATUS
        # --------------------------------------------------

        print("\nProject Status:")
        print("1. Planning")
        print("2. Active")
        print("3. Completed")
        print("4. On Hold")

        status_map = {
            "1": "Planning",
            "2": "Active",
            "3": "Completed",
            "4": "On Hold"
        }

        status_choice = input(
            "Enter Status: "
        ).strip()

        if status_choice not in status_map:

            print("\n❌ Invalid status!")

            cursor.close()
            connection.close()
            return

        status = status_map[status_choice]

        # --------------------------------------------------
        # INSERT PROJECT
        # --------------------------------------------------

        cursor.execute("""
            INSERT INTO projects
            (
                project_code,
                project_name,
                client_name,
                description,
                start_date,
                end_date,
                status
            )
            VALUES
            (%s, %s, %s, %s, %s, %s, %s)
        """, (
            project_code,
            project_name,
            client_name if client_name else None,
            description if description else None,
            start_date,
            end_date,
            status
        ))

        connection.commit()

        print("\n")
        print("=" * 70)
        print("                ✅ PROJECT CREATED")
        print("=" * 70)

        print(f"Project ID   : {cursor.lastrowid}")
        print(f"Project Code : {project_code}")
        print(f"Project Name : {project_name}")
        print(f"Client       : {client_name if client_name else '--'}")
        print(f"Start Date   : {start_date}")
        print(
            f"End Date     : "
            f"{end_date if end_date else '--'}"
        )
        print(f"Status       : {status}")

        print("=" * 70)

        cursor.close()
        connection.close()

    except Exception as e:

        connection.rollback()

        print(f"\n❌ Error creating project: {e}")

        if connection.is_connected():
            connection.close()


# ============================================================
# ADMIN - VIEW ALL PROJECTS
# ============================================================

def view_all_projects():

    connection = create_connection()

    if connection is None:
        return

    try:

        cursor = connection.cursor(dictionary=True)

        cursor.execute("""
            SELECT
                p.project_id,
                p.project_code,
                p.project_name,
                p.client_name,
                p.start_date,
                p.end_date,
                p.status,
                COUNT(
                    CASE
                        WHEN ep.status = 'Active'
                        THEN ep.assignment_id
                    END
                ) AS active_employees
            FROM projects p
            LEFT JOIN employee_projects ep
                ON p.project_id = ep.project_id
            GROUP BY
                p.project_id,
                p.project_code,
                p.project_name,
                p.client_name,
                p.start_date,
                p.end_date,
                p.status
            ORDER BY p.project_id DESC
        """)

        projects = cursor.fetchall()

        print("\n")
        print("=" * 125)
        print(" " * 50 + "ALL PROJECTS")
        print("=" * 125)

        if not projects:

            print("\n❌ No projects found.")
            print("=" * 125)

            cursor.close()
            connection.close()
            return

        print(
            f"{'ID':<7}"
            f"{'CODE':<12}"
            f"{'PROJECT NAME':<25}"
            f"{'CLIENT':<20}"
            f"{'START':<13}"
            f"{'END':<13}"
            f"{'STATUS':<13}"
            f"{'EMPLOYEES':<10}"
        )

        print("-" * 125)

        for project in projects:

            project_name = project["project_name"]
            client_name = project["client_name"]

            if len(project_name) > 22:
                project_name = project_name[:19] + "..."

            if not client_name:
                client_name = "--"
            elif len(client_name) > 17:
                client_name = client_name[:14] + "..."

            print(
                f"{project['project_id']:<7}"
                f"{project['project_code']:<12}"
                f"{project_name:<25}"
                f"{client_name:<20}"
                f"{str(project['start_date']):<13}"
                f"{str(project['end_date']) if project['end_date'] else '--':<13}"
                f"{project['status']:<13}"
                f"{project['active_employees']:<10}"
            )

        print("-" * 125)

        cursor.close()
        connection.close()

    except Exception as e:

        print(f"\n❌ Error loading projects: {e}")

        if connection.is_connected():
            connection.close()


# ============================================================
# ADMIN - SEARCH PROJECT
# ============================================================

def search_project():

    connection = create_connection()

    if connection is None:
        return

    try:

        cursor = connection.cursor(dictionary=True)

        print("\n")
        print("=" * 70)
        print("                      SEARCH PROJECT")
        print("=" * 70)

        search_text = input(
            "Enter Project Code / Name / Client: "
        ).strip()

        if search_text == "":

            print("\n❌ Search value cannot be empty!")

            cursor.close()
            connection.close()
            return

        search_pattern = f"%{search_text}%"

        cursor.execute("""
            SELECT
                project_id,
                project_code,
                project_name,
                client_name,
                start_date,
                end_date,
                status
            FROM projects
            WHERE project_code LIKE %s
               OR project_name LIKE %s
               OR client_name LIKE %s
            ORDER BY project_id DESC
        """, (
            search_pattern,
            search_pattern,
            search_pattern
        ))

        projects = cursor.fetchall()

        print("\n")

        if not projects:

            print("❌ No matching projects found.")

        else:

            print("=" * 110)
            print("                      SEARCH RESULTS")
            print("=" * 110)

            print(
                f"{'ID':<7}"
                f"{'CODE':<12}"
                f"{'PROJECT NAME':<25}"
                f"{'CLIENT':<20}"
                f"{'START':<13}"
                f"{'END':<13}"
                f"{'STATUS':<13}"
            )

            print("-" * 110)

            for project in projects:

                project_name = project["project_name"]
                client_name = project["client_name"]

                if len(project_name) > 22:
                    project_name = project_name[:19] + "..."

                if not client_name:
                    client_name = "--"
                elif len(client_name) > 17:
                    client_name = client_name[:14] + "..."

                print(
                    f"{project['project_id']:<7}"
                    f"{project['project_code']:<12}"
                    f"{project_name:<25}"
                    f"{client_name:<20}"
                    f"{str(project['start_date']):<13}"
                    f"{str(project['end_date']) if project['end_date'] else '--':<13}"
                    f"{project['status']:<13}"
                )

            print("-" * 110)

        cursor.close()
        connection.close()

    except Exception as e:

        print(f"\n❌ Error searching projects: {e}")

        if connection.is_connected():
            connection.close()


# ============================================================
# ADMIN - VIEW PROJECT DETAILS
# ============================================================

def view_project_details():

    connection = create_connection()

    if connection is None:
        return

    try:

        cursor = connection.cursor(dictionary=True)

        print("\n")
        print("=" * 70)
        print("                    PROJECT DETAILS")
        print("=" * 70)

        project_code = input(
            "Enter Project Code: "
        ).strip()

        cursor.execute("""
            SELECT
                p.project_id,
                p.project_code,
                p.project_name,
                p.client_name,
                p.description,
                p.start_date,
                p.end_date,
                p.status,
                p.created_at
            FROM projects p
            WHERE p.project_code = %s
        """, (project_code,))

        project = cursor.fetchone()

        if project is None:

            print("\n❌ Project not found!")

            cursor.close()
            connection.close()
            return

        cursor.execute("""
            SELECT
                e.employee_code,
                e.full_name,
                d.department_name,
                ep.project_role,
                ep.allocation_percentage,
                ep.assigned_date,
                ep.removed_date,
                ep.status
            FROM employee_projects ep
            INNER JOIN employees e
                ON ep.employee_id = e.employee_id
            INNER JOIN departments d
                ON e.department_id = d.department_id
            WHERE ep.project_id = %s
            ORDER BY ep.status, e.full_name
        """, (project["project_id"],))

        employees = cursor.fetchall()

        print("\n")
        print("=" * 70)
        print("                    PROJECT DETAILS")
        print("=" * 70)

        print(f"Project ID   : {project['project_id']}")
        print(f"Project Code : {project['project_code']}")
        print(f"Project Name : {project['project_name']}")
        print(
            f"Client       : "
            f"{project['client_name'] if project['client_name'] else '--'}"
        )

        print(
            f"Description  : "
            f"{project['description'] if project['description'] else '--'}"
        )

        print(f"Start Date   : {project['start_date']}")
        print(
            f"End Date     : "
            f"{project['end_date'] if project['end_date'] else '--'}"
        )
        print(f"Status       : {project['status']}")
        print(f"Created At   : {project['created_at']}")

        print("-" * 70)
        print("ASSIGNED EMPLOYEES")
        print("-" * 70)

        if not employees:

            print("No employees assigned.")

        else:

            print(
                f"{'EMP ID':<12}"
                f"{'NAME':<22}"
                f"{'ROLE':<20}"
                f"{'ALLOC %':<10}"
                f"{'STATUS':<12}"
            )

            print("-" * 70)

            for employee in employees:

                role = employee["project_role"]

                if len(role) > 17:
                    role = role[:14] + "..."

                print(
                    f"{employee['employee_code']:<12}"
                    f"{employee['full_name']:<22}"
                    f"{role:<20}"
                    f"{str(employee['allocation_percentage']):<10}"
                    f"{employee['status']:<12}"
                )

        print("=" * 70)

        cursor.close()
        connection.close()

    except Exception as e:

        print(f"\n❌ Error loading project details: {e}")

        if connection.is_connected():
            connection.close()


# ============================================================
# ADMIN - UPDATE PROJECT
# ============================================================

def update_project():

    connection = create_connection()

    if connection is None:
        return

    try:

        cursor = connection.cursor(dictionary=True)

        print("\n")
        print("=" * 70)
        print("                     UPDATE PROJECT")
        print("=" * 70)

        project_code = input(
            "Enter Project Code: "
        ).strip()

        cursor.execute("""
            SELECT *
            FROM projects
            WHERE project_code = %s
        """, (project_code,))

        project = cursor.fetchone()

        if project is None:

            print("\n❌ Project not found!")

            cursor.close()
            connection.close()
            return

        print("\nPress Enter to keep the existing value.\n")

        # --------------------------------------------------
        # PROJECT NAME
        # --------------------------------------------------

        project_name = input(
            f"Project Name [{project['project_name']}]: "
        ).strip()

        if project_name == "":
            project_name = project["project_name"]

        # --------------------------------------------------
        # CLIENT
        # --------------------------------------------------

        current_client = project["client_name"] or ""

        client_name = input(
            f"Client Name [{current_client}]: "
        ).strip()

        if client_name == "":
            client_name = project["client_name"]

        # --------------------------------------------------
        # DESCRIPTION
        # --------------------------------------------------

        current_description = project["description"] or ""

        description = input(
            f"Description [{current_description}]: "
        ).strip()

        if description == "":
            description = project["description"]

        # --------------------------------------------------
        # START DATE
        # --------------------------------------------------

        while True:

            current_start = str(project["start_date"])

            start_input = input(
                f"Start Date [{current_start}]: "
            ).strip()

            if start_input == "":
                start_date = project["start_date"]
                break

            try:

                start_date = datetime.strptime(
                    start_input,
                    "%Y-%m-%d"
                ).date()

                break

            except ValueError:

                print(
                    "❌ Invalid date format! Use YYYY-MM-DD."
                )

        # --------------------------------------------------
        # END DATE
        # --------------------------------------------------

        while True:

            current_end = (
                str(project["end_date"])
                if project["end_date"]
                else ""
            )

            end_input = input(
                f"End Date [{current_end}]: "
            ).strip()

            if end_input == "":
                end_date = project["end_date"]
                break

            try:

                end_date = datetime.strptime(
                    end_input,
                    "%Y-%m-%d"
                ).date()

                if end_date < start_date:

                    print(
                        "❌ End date cannot be before start date!"
                    )
                    continue

                break

            except ValueError:

                print(
                    "❌ Invalid date format! Use YYYY-MM-DD."
                )

        # --------------------------------------------------
        # STATUS
        # --------------------------------------------------

        print("\nCurrent Status:", project["status"])
        print("1. Planning")
        print("2. Active")
        print("3. Completed")
        print("4. On Hold")

        status_input = input(
            "Enter new status (or Enter to keep current): "
        ).strip()

        status_map = {
            "1": "Planning",
            "2": "Active",
            "3": "Completed",
            "4": "On Hold"
        }

        if status_input == "":
            status = project["status"]

        elif status_input in status_map:
            status = status_map[status_input]

        else:

            print("\n❌ Invalid status!")

            cursor.close()
            connection.close()
            return

        # --------------------------------------------------
        # UPDATE
        # --------------------------------------------------

        cursor.execute("""
            UPDATE projects
            SET
                project_name = %s,
                client_name = %s,
                description = %s,
                start_date = %s,
                end_date = %s,
                status = %s
            WHERE project_id = %s
        """, (
            project_name,
            client_name,
            description,
            start_date,
            end_date,
            status,
            project["project_id"]
        ))

        connection.commit()

        print("\n✅ Project updated successfully!")

        cursor.close()
        connection.close()

    except Exception as e:

        connection.rollback()

        print(f"\n❌ Error updating project: {e}")

        if connection.is_connected():
            connection.close()


# ============================================================
# ADMIN - ASSIGN EMPLOYEE TO PROJECT
# ============================================================

def assign_employee_to_project():

    connection = create_connection()

    if connection is None:
        return

    try:

        cursor = connection.cursor(dictionary=True)

        print("\n")
        print("=" * 70)
        print("                 ASSIGN EMPLOYEE TO PROJECT")
        print("=" * 70)

        employee_code = input(
            "Enter Employee Code: "
        ).strip()

        employee = get_employee_by_code(employee_code)

        if employee is None:

            print("\n❌ Employee not found!")

            cursor.close()
            connection.close()
            return

        if employee["status"] == "Inactive":

            print("\n❌ Inactive employee cannot be assigned!")

            cursor.close()
            connection.close()
            return

        project_code = input(
            "Enter Project Code: "
        ).strip()

        project = get_project_by_code(project_code)

        if project is None:

            print("\n❌ Project not found!")

            cursor.close()
            connection.close()
            return

        if project["status"] in ("Completed", "On Hold"):

            print(
                f"\n❌ Cannot assign employee to a "
                f"{project['status']} project!"
            )

            cursor.close()
            connection.close()
            return

        # --------------------------------------------------
        # CHECK ACTIVE DUPLICATE
        # --------------------------------------------------

        cursor.execute("""
            SELECT
                assignment_id
            FROM employee_projects
            WHERE employee_id = %s
            AND project_id = %s
            AND status = 'Active'
        """, (
            employee["employee_id"],
            project["project_id"]
        ))

        existing_assignment = cursor.fetchone()

        if existing_assignment is not None:

            print(
                "\n❌ Employee is already actively assigned "
                "to this project!"
            )

            cursor.close()
            connection.close()
            return

        # --------------------------------------------------
        # PROJECT ROLE
        # --------------------------------------------------

        while True:

            project_role = input(
                "Enter Project Role: "
            ).strip()

            if project_role == "":
                print("❌ Project role cannot be empty!")
                continue

            if len(project_role) > 100:
                print(
                    "❌ Project role cannot exceed 100 characters!"
                )
                continue

            break

        # --------------------------------------------------
        # ALLOCATION
        # --------------------------------------------------

        while True:

            allocation_input = input(
                "Enter Allocation Percentage (1-100): "
            ).strip()

            try:

                allocation = float(allocation_input)

                if allocation <= 0 or allocation > 100:

                    print(
                        "❌ Allocation must be between 1 and 100."
                    )
                    continue

                allocation = round(allocation, 2)

                break

            except ValueError:

                print(
                    "❌ Enter a valid percentage."
                )

        # --------------------------------------------------
        # ASSIGNED DATE
        # --------------------------------------------------

        while True:

            assigned_date_input = input(
                "Enter Assigned Date (YYYY-MM-DD): "
            ).strip()

            try:

                assigned_date = datetime.strptime(
                    assigned_date_input,
                    "%Y-%m-%d"
                ).date()

                if assigned_date < project["start_date"]:

                    print(
                        "❌ Assigned date cannot be before "
                        "project start date!"
                    )
                    continue

                if (
                    project["end_date"] is not None
                    and assigned_date > project["end_date"]
                ):

                    print(
                        "❌ Assigned date cannot be after "
                        "project end date!"
                    )
                    continue

                break

            except ValueError:

                print(
                    "❌ Invalid date format! Use YYYY-MM-DD."
                )

        # --------------------------------------------------
        # INSERT ASSIGNMENT
        # --------------------------------------------------

        cursor.execute("""
            INSERT INTO employee_projects
            (
                employee_id,
                project_id,
                project_role,
                allocation_percentage,
                assigned_date,
                status
            )
            VALUES
            (%s, %s, %s, %s, %s, 'Active')
        """, (
            employee["employee_id"],
            project["project_id"],
            project_role,
            allocation,
            assigned_date
        ))

        connection.commit()

        print("\n")
        print("=" * 70)
        print("             ✅ EMPLOYEE ASSIGNED SUCCESSFULLY")
        print("=" * 70)

        print(f"Employee     : {employee['employee_code']}")
        print(f"Name         : {employee['full_name']}")
        print(f"Project      : {project['project_code']}")
        print(f"Project Name : {project['project_name']}")
        print(f"Project Role : {project_role}")
        print(f"Allocation   : {allocation}%")
        print(f"Assigned Date: {assigned_date}")
        print("Status       : Active")

        print("=" * 70)

        cursor.close()
        connection.close()

    except Exception as e:

        connection.rollback()

        print(f"\n❌ Error assigning employee: {e}")

        if connection.is_connected():
            connection.close()


# ============================================================
# ADMIN - VIEW PROJECT EMPLOYEES
# ============================================================

def view_project_employees():

    connection = create_connection()

    if connection is None:
        return

    try:

        cursor = connection.cursor(dictionary=True)

        print("\n")
        print("=" * 70)
        print("                  PROJECT EMPLOYEES")
        print("=" * 70)

        project_code = input(
            "Enter Project Code: "
        ).strip()

        cursor.execute("""
            SELECT
                p.project_id,
                p.project_code,
                p.project_name
            FROM projects p
            WHERE p.project_code = %s
        """, (project_code,))

        project = cursor.fetchone()

        if project is None:

            print("\n❌ Project not found!")

            cursor.close()
            connection.close()
            return

        cursor.execute("""
            SELECT
                ep.assignment_id,
                e.employee_code,
                e.full_name,
                d.department_name,
                ep.project_role,
                ep.allocation_percentage,
                ep.assigned_date,
                ep.removed_date,
                ep.status
            FROM employee_projects ep
            INNER JOIN employees e
                ON ep.employee_id = e.employee_id
            INNER JOIN departments d
                ON e.department_id = d.department_id
            WHERE ep.project_id = %s
            ORDER BY ep.status, e.full_name
        """, (project["project_id"],))

        employees = cursor.fetchall()

        print("\n")
        print("=" * 110)
        print(
            f"PROJECT: {project['project_code']} - "
            f"{project['project_name']}"
        )
        print("=" * 110)

        if not employees:

            print("\n❌ No employees assigned to this project.")

            print("=" * 110)

            cursor.close()
            connection.close()
            return

        print(
            f"{'ID':<7}"
            f"{'EMP ID':<12}"
            f"{'NAME':<22}"
            f"{'ROLE':<20}"
            f"{'ALLOC %':<10}"
            f"{'ASSIGNED':<13}"
            f"{'STATUS':<12}"
        )

        print("-" * 110)

        for employee in employees:

            role = employee["project_role"]

            if len(role) > 17:
                role = role[:14] + "..."

            print(
                f"{employee['assignment_id']:<7}"
                f"{employee['employee_code']:<12}"
                f"{employee['full_name']:<22}"
                f"{role:<20}"
                f"{str(employee['allocation_percentage']):<10}"
                f"{str(employee['assigned_date']):<13}"
                f"{employee['status']:<12}"
            )

        print("-" * 110)

        cursor.close()
        connection.close()

    except Exception as e:

        print(f"\n❌ Error loading project employees: {e}")

        if connection.is_connected():
            connection.close()


# ============================================================
# EMPLOYEE - VIEW MY PROJECTS
# ============================================================

def view_my_projects(employee_code):

    employee = get_employee_by_code(employee_code)

    if employee is None:

        print("\n❌ Employee not found!")
        return

    connection = create_connection()

    if connection is None:
        return

    try:

        cursor = connection.cursor(dictionary=True)

        cursor.execute("""
            SELECT
                p.project_code,
                p.project_name,
                p.client_name,
                p.start_date,
                p.end_date,
                p.status AS project_status,
                ep.project_role,
                ep.allocation_percentage,
                ep.assigned_date,
                ep.removed_date,
                ep.status AS assignment_status
            FROM employee_projects ep
            INNER JOIN projects p
                ON ep.project_id = p.project_id
            WHERE ep.employee_id = %s
            ORDER BY ep.status, ep.assigned_date DESC
        """, (employee["employee_id"],))

        projects = cursor.fetchall()

        print("\n")
        print("=" * 120)
        print(" " * 45 + "MY PROJECTS")
        print("=" * 120)

        print(
            f"Employee ID : {employee['employee_code']}"
        )

        print(
            f"Name        : {employee['full_name']}"
        )

        print("-" * 120)

        if not projects:

            print("\n❌ No projects assigned.")

            print("=" * 120)

            cursor.close()
            connection.close()
            return

        print(
            f"{'CODE':<12}"
            f"{'PROJECT':<25}"
            f"{'ROLE':<20}"
            f"{'ALLOC %':<10}"
            f"{'START':<13}"
            f"{'END':<13}"
            f"{'STATUS':<12}"
        )

        print("-" * 120)

        for project in projects:

            project_name = project["project_name"]
            role = project["project_role"]

            if len(project_name) > 22:
                project_name = project_name[:19] + "..."

            if len(role) > 17:
                role = role[:14] + "..."

            print(
                f"{project['project_code']:<12}"
                f"{project_name:<25}"
                f"{role:<20}"
                f"{str(project['allocation_percentage']):<10}"
                f"{str(project['start_date']):<13}"
                f"{str(project['end_date']) if project['end_date'] else '--':<13}"
                f"{project['assignment_status']:<12}"
            )

        print("-" * 120)

        cursor.close()
        connection.close()

    except Exception as e:

        print(f"\n❌ Error loading your projects: {e}")

        if connection.is_connected():
            connection.close()


# ============================================================
# ADMIN - REMOVE EMPLOYEE FROM PROJECT
# ============================================================

def remove_employee_from_project():

    connection = create_connection()

    if connection is None:
        return

    try:

        cursor = connection.cursor(dictionary=True)

        print("\n")
        print("=" * 70)
        print("                REMOVE EMPLOYEE FROM PROJECT")
        print("=" * 70)

        employee_code = input(
            "Enter Employee Code: "
        ).strip()

        employee = get_employee_by_code(employee_code)

        if employee is None:

            print("\n❌ Employee not found!")

            cursor.close()
            connection.close()
            return

        project_code = input(
            "Enter Project Code: "
        ).strip()

        project = get_project_by_code(project_code)

        if project is None:

            print("\n❌ Project not found!")

            cursor.close()
            connection.close()
            return

        cursor.execute("""
            SELECT
                assignment_id,
                project_role,
                allocation_percentage,
                assigned_date,
                status
            FROM employee_projects
            WHERE employee_id = %s
            AND project_id = %s
            AND status = 'Active'
            LIMIT 1
        """, (
            employee["employee_id"],
            project["project_id"]
        ))

        assignment = cursor.fetchone()

        if assignment is None:

            print(
                "\n❌ Employee does not have an active "
                "assignment on this project!"
            )

            cursor.close()
            connection.close()
            return

        print("\nAssignment Details:")
        print(f"Employee : {employee['employee_code']}")
        print(f"Project  : {project['project_code']}")
        print(f"Role     : {assignment['project_role']}")
        print(
            f"Allocation: "
            f"{assignment['allocation_percentage']}%"
        )

        confirmation = input(
            "\nAre you sure you want to remove this employee? (Y/N): "
        ).strip().upper()

        if confirmation != "Y":

            print("\n❌ Operation cancelled.")

            cursor.close()
            connection.close()
            return

        removed_date = datetime.now().date()

        cursor.execute("""
            UPDATE employee_projects
            SET
                removed_date = %s,
                status = 'Removed'
            WHERE assignment_id = %s
        """, (
            removed_date,
            assignment["assignment_id"]
        ))

        connection.commit()

        print("\n")
        print("=" * 70)
        print("          ✅ EMPLOYEE REMOVED FROM PROJECT")
        print("=" * 70)

        print(f"Employee     : {employee['employee_code']}")
        print(f"Project      : {project['project_code']}")
        print(f"Project Role : {assignment['project_role']}")
        print(f"Removed Date : {removed_date}")
        print("Status       : Removed")

        print("=" * 70)

        cursor.close()
        connection.close()

    except Exception as e:

        connection.rollback()

        print(
            f"\n❌ Error removing employee from project: {e}"
        )

        if connection.is_connected():
            connection.close()


# ============================================================
# ADMIN - MARK ASSIGNMENT COMPLETED
# ============================================================

def complete_employee_assignment():

    connection = create_connection()

    if connection is None:
        return

    try:

        cursor = connection.cursor(dictionary=True)

        print("\n")
        print("=" * 70)
        print("              COMPLETE PROJECT ASSIGNMENT")
        print("=" * 70)

        employee_code = input(
            "Enter Employee Code: "
        ).strip()

        employee = get_employee_by_code(employee_code)

        if employee is None:

            print("\n❌ Employee not found!")

            cursor.close()
            connection.close()
            return

        project_code = input(
            "Enter Project Code: "
        ).strip()

        project = get_project_by_code(project_code)

        if project is None:

            print("\n❌ Project not found!")

            cursor.close()
            connection.close()
            return

        cursor.execute("""
            SELECT
                assignment_id,
                project_role,
                allocation_percentage,
                assigned_date,
                status
            FROM employee_projects
            WHERE employee_id = %s
            AND project_id = %s
            AND status = 'Active'
            LIMIT 1
        """, (
            employee["employee_id"],
            project["project_id"]
        ))

        assignment = cursor.fetchone()

        if assignment is None:

            print(
                "\n❌ No active assignment found!"
            )

            cursor.close()
            connection.close()
            return

        completion_date = datetime.now().date()

        cursor.execute("""
            UPDATE employee_projects
            SET
                removed_date = %s,
                status = 'Completed'
            WHERE assignment_id = %s
        """, (
            completion_date,
            assignment["assignment_id"]
        ))

        connection.commit()

        print("\n")
        print("=" * 70)
        print("          ✅ PROJECT ASSIGNMENT COMPLETED")
        print("=" * 70)

        print(f"Employee     : {employee['employee_code']}")
        print(f"Project      : {project['project_code']}")
        print(f"Project Role : {assignment['project_role']}")
        print(f"Completed On : {completion_date}")
        print("Status       : Completed")

        print("=" * 70)

        cursor.close()
        connection.close()

    except Exception as e:

        connection.rollback()

        print(
            f"\n❌ Error completing assignment: {e}"
        )

        if connection.is_connected():
            connection.close()


# ============================================================
# PROJECT MANAGEMENT MENU
# ============================================================

def project_management_menu():

    while True:

        print("\n")
        print("=" * 70)
        print("                    PROJECT MANAGEMENT")
        print("=" * 70)

        print("1. Add Project")
        print("2. View All Projects")
        print("3. Search Project")
        print("4. View Project Details")
        print("5. Update Project")
        print("6. Assign Employee to Project")
        print("7. View Project Employees")
        print("8. Remove Employee from Project")
        print("9. Complete Employee Assignment")
        print("10. Back")

        print("=" * 70)

        choice = input(
            "Enter your choice: "
        ).strip()

        if choice == "1":
            add_project()

        elif choice == "2":
            view_all_projects()

        elif choice == "3":
            search_project()

        elif choice == "4":
            view_project_details()

        elif choice == "5":
            update_project()

        elif choice == "6":
            assign_employee_to_project()

        elif choice == "7":
            view_project_employees()

        elif choice == "8":
            remove_employee_from_project()

        elif choice == "9":
            complete_employee_assignment()

        elif choice == "10":
            break

        else:
            print("\n❌ Invalid choice!")





if __name__ == "__main__":
    view_my_projects("EMP1001")           