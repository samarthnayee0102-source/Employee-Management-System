from database import create_connection


# ============================================================
# 1. EMPLOYEE REPORT
# ============================================================

def employee_report():
    connection = create_connection()

    if connection is None:
        return

    try:
        cursor = connection.cursor(dictionary=True)

        # Total employees by status
        cursor.execute("""
            SELECT
                status,
                COUNT(*) AS total
            FROM employees
            GROUP BY status
            ORDER BY status
        """)

        status_data = cursor.fetchall()

        # Department-wise employee count
        cursor.execute("""
            SELECT
                d.department_name,
                COUNT(e.employee_id) AS total_employees
            FROM departments d
            LEFT JOIN employees e
                ON d.department_id = e.department_id
            GROUP BY d.department_id, d.department_name
            ORDER BY d.department_name
        """)

        department_data = cursor.fetchall()

        # Employee details
        cursor.execute("""
            SELECT
                e.employee_code,
                e.full_name,
                d.department_name,
                e.designation,
                e.salary,
                e.joining_date,
                e.status
            FROM employees e
            JOIN departments d
                ON e.department_id = d.department_id
            ORDER BY e.employee_id DESC
        """)

        employees = cursor.fetchall()

        print("\n" + "=" * 85)
        print("                       EMPLOYEE REPORT")
        print("=" * 85)

        print("\n📊 EMPLOYEE STATUS")
        print("-" * 50)

        for row in status_data:
            print(f"{row['status']:<15} : {row['total']}")

        print("\n🏢 DEPARTMENT-WISE EMPLOYEES")
        print("-" * 50)

        for row in department_data:
            print(
                f"{row['department_name']:<25} : "
                f"{row['total_employees']}"
            )

        print("\n👥 EMPLOYEE DETAILS")
        print("-" * 85)

        if employees:
            print(
                f"{'Code':<12}"
                f"{'Name':<22}"
                f"{'Department':<18}"
                f"{'Designation':<18}"
                f"{'Status':<12}"
            )

            print("-" * 85)

            for employee in employees:
                print(
                    f"{employee['employee_code']:<12}"
                    f"{employee['full_name'][:20]:<22}"
                    f"{employee['department_name'][:16]:<18}"
                    f"{employee['designation'][:16]:<18}"
                    f"{employee['status']:<12}"
                )
        else:
            print("No employees found.")

        print("=" * 85)

        cursor.close()
        connection.close()

    except Exception as e:
        print(f"❌ Employee report error: {e}")

        if connection.is_connected():
            connection.close()


# ============================================================
# 2. ATTENDANCE REPORT
# ============================================================

def attendance_report():
    connection = create_connection()

    if connection is None:
        return

    try:
        cursor = connection.cursor(dictionary=True)

        print("\n" + "=" * 85)
        print("                      ATTENDANCE REPORT")
        print("=" * 85)

        employee_code = input(
            "\nEnter Employee Code (or press Enter for all): "
        ).strip()

        if employee_code:

            query = """
                SELECT
                    e.employee_code,
                    e.full_name,
                    d.department_name,
                    a.attendance_date,
                    a.check_in,
                    a.check_out,
                    a.status,
                    a.working_hours,
                    a.remarks
                FROM attendance a
                JOIN employees e
                    ON a.employee_id = e.employee_id
                JOIN departments d
                    ON e.department_id = d.department_id
                WHERE e.employee_code = %s
                ORDER BY a.attendance_date DESC
            """

            cursor.execute(query, (employee_code,))

        else:

            query = """
                SELECT
                    e.employee_code,
                    e.full_name,
                    d.department_name,
                    a.attendance_date,
                    a.check_in,
                    a.check_out,
                    a.status,
                    a.working_hours,
                    a.remarks
                FROM attendance a
                JOIN employees e
                    ON a.employee_id = e.employee_id
                JOIN departments d
                    ON e.department_id = d.department_id
                ORDER BY a.attendance_date DESC
                LIMIT 100
            """

            cursor.execute(query)

        records = cursor.fetchall()

        if not records:
            print("\n📭 No attendance records found.")
        else:

            print("\n" + "-" * 100)

            print(
                f"{'Code':<11}"
                f"{'Name':<20}"
                f"{'Date':<12}"
                f"{'In':<10}"
                f"{'Out':<10}"
                f"{'Status':<12}"
                f"{'Hours':<8}"
            )

            print("-" * 100)

            for record in records:

                check_in = (
                    str(record["check_in"])
                    if record["check_in"]
                    else "-"
                )

                check_out = (
                    str(record["check_out"])
                    if record["check_out"]
                    else "-"
                )

                hours = (
                    str(record["working_hours"])
                    if record["working_hours"] is not None
                    else "-"
                )

                print(
                    f"{record['employee_code']:<11}"
                    f"{record['full_name'][:18]:<20}"
                    f"{str(record['attendance_date']):<12}"
                    f"{check_in:<10}"
                    f"{check_out:<10}"
                    f"{record['status']:<12}"
                    f"{hours:<8}"
                )

            print("-" * 100)

            # Summary
            if employee_code:
                cursor.execute("""
                    SELECT
                        COUNT(*) AS total_days,
                        SUM(status = 'Present') AS present_days,
                        SUM(status = 'Late') AS late_days,
                        SUM(status = 'Absent') AS absent_days,
                        COALESCE(SUM(working_hours), 0) AS total_hours
                    FROM attendance a
                    JOIN employees e
                        ON a.employee_id = e.employee_id
                    WHERE e.employee_code = %s
                """, (employee_code,))

                summary = cursor.fetchone()

                print("\n📊 SUMMARY")
                print("-" * 50)
                print(f"Total Attendance Records : {summary['total_days']}")
                print(f"Present                   : {summary['present_days'] or 0}")
                print(f"Late                      : {summary['late_days'] or 0}")
                print(f"Absent                    : {summary['absent_days'] or 0}")
                print(f"Total Working Hours       : {summary['total_hours']:.2f}")

        print("=" * 85)

        cursor.close()
        connection.close()

    except Exception as e:
        print(f"❌ Attendance report error: {e}")

        if connection.is_connected():
            connection.close()


# ============================================================
# 3. LEAVE REPORT
# ============================================================

def leave_report():
    connection = create_connection()

    if connection is None:
        return

    try:
        cursor = connection.cursor(dictionary=True)

        # Leave status summary
        cursor.execute("""
            SELECT
                status,
                COUNT(*) AS total_requests,
                COALESCE(SUM(total_days), 0) AS total_days
            FROM leave_requests
            GROUP BY status
            ORDER BY status
        """)

        status_data = cursor.fetchall()

        # Leave type summary
        cursor.execute("""
            SELECT
                leave_type,
                COUNT(*) AS total_requests,
                COALESCE(SUM(total_days), 0) AS total_days
            FROM leave_requests
            GROUP BY leave_type
            ORDER BY leave_type
        """)

        type_data = cursor.fetchall()

        # Detailed requests
        cursor.execute("""
            SELECT
                lr.leave_id,
                e.employee_code,
                e.full_name,
                lr.leave_type,
                lr.start_date,
                lr.end_date,
                lr.total_days,
                lr.status,
                lr.reason
            FROM leave_requests lr
            JOIN employees e
                ON lr.employee_id = e.employee_id
            ORDER BY lr.applied_at DESC
        """)

        requests = cursor.fetchall()

        print("\n" + "=" * 100)
        print("                         LEAVE REPORT")
        print("=" * 100)

        print("\n📊 LEAVE STATUS SUMMARY")
        print("-" * 60)

        for row in status_data:
            print(
                f"{row['status']:<15}"
                f" Requests: {row['total_requests']:<5}"
                f" Days: {row['total_days']}"
            )

        print("\n🏖️ LEAVE TYPE SUMMARY")
        print("-" * 60)

        for row in type_data:
            print(
                f"{row['leave_type']:<20}"
                f" Requests: {row['total_requests']:<5}"
                f" Days: {row['total_days']}"
            )

        print("\n📝 LEAVE REQUEST DETAILS")
        print("-" * 100)

        if requests:

            print(
                f"{'ID':<5}"
                f"{'Code':<11}"
                f"{'Name':<20}"
                f"{'Type':<18}"
                f"{'Days':<6}"
                f"{'Status':<12}"
            )

            print("-" * 100)

            for request in requests:

                print(
                    f"{request['leave_id']:<5}"
                    f"{request['employee_code']:<11}"
                    f"{request['full_name'][:18]:<20}"
                    f"{request['leave_type'][:16]:<18}"
                    f"{request['total_days']:<6}"
                    f"{request['status']:<12}"
                )

        else:
            print("No leave requests found.")

        print("=" * 100)

        cursor.close()
        connection.close()

    except Exception as e:
        print(f"❌ Leave report error: {e}")

        if connection.is_connected():
            connection.close()


# ============================================================
# 4. PROJECT REPORT
# ============================================================

def project_report():
    connection = create_connection()

    if connection is None:
        return

    try:
        cursor = connection.cursor(dictionary=True)

        # Project status summary
        cursor.execute("""
            SELECT
                status,
                COUNT(*) AS total_projects
            FROM projects
            GROUP BY status
            ORDER BY status
        """)

        status_data = cursor.fetchall()

        # Project details with active employee count
        cursor.execute("""
            SELECT
                p.project_code,
                p.project_name,
                p.client_name,
                p.start_date,
                p.end_date,
                p.status,
                COUNT(
                    CASE
                        WHEN ep.status = 'Active'
                        THEN ep.employee_id
                    END
                ) AS assigned_employees
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

        print("\n" + "=" * 100)
        print("                         PROJECT REPORT")
        print("=" * 100)

        print("\n📊 PROJECT STATUS SUMMARY")
        print("-" * 60)

        for row in status_data:
            print(
                f"{row['status']:<15} : "
                f"{row['total_projects']}"
            )

        print("\n📁 PROJECT DETAILS")
        print("-" * 100)

        if projects:

            print(
                f"{'Code':<12}"
                f"{'Project Name':<25}"
                f"{'Client':<20}"
                f"{'Status':<15}"
                f"{'Employees':<10}"
            )

            print("-" * 100)

            for project in projects:

                print(
                    f"{project['project_code']:<12}"
                    f"{project['project_name'][:23]:<25}"
                    f"{str(project['client_name'] or 'N/A')[:18]:<20}"
                    f"{project['status']:<15}"
                    f"{project['assigned_employees']:<10}"
                )

        else:
            print("No projects found.")

        print("=" * 100)

        cursor.close()
        connection.close()

    except Exception as e:
        print(f"❌ Project report error: {e}")

        if connection.is_connected():
            connection.close()


# ============================================================
# REPORT MENU
# ============================================================

def report_menu():
    while True:

        print("\n" + "=" * 60)
        print("                    REPORTS")
        print("=" * 60)

        print("1. Employee Report")
        print("2. Attendance Report")
        print("3. Leave Report")
        print("4. Project Report")
        print("5. Back")

        print("=" * 60)

        choice = input("Enter your choice: ").strip()

        if choice == "1":
            employee_report()
            input("\nPress Enter to continue...")

        elif choice == "2":
            attendance_report()
            input("\nPress Enter to continue...")

        elif choice == "3":
            leave_report()
            input("\nPress Enter to continue...")

        elif choice == "4":
            project_report()
            input("\nPress Enter to continue...")

        elif choice == "5":
            break

        else:
            print("❌ Invalid choice!")


# ============================================================
# DIRECT TEST
# ============================================================

if __name__ == "__main__":
    report_menu()