from database import create_connection


def show_dashboard():
    connection = create_connection()

    if connection is None:
        print("❌ Database connection failed!")
        return

    try:
        cursor = connection.cursor(dictionary=True)

        # =========================================================
        # 1. TOTAL ACTIVE EMPLOYEES
        # =========================================================
        cursor.execute("""
            SELECT COUNT(*) AS total_employees
            FROM employees
            WHERE status = 'Active'
        """)
        total_employees = cursor.fetchone()["total_employees"]

        # =========================================================
        # 2. TOTAL DEPARTMENTS
        # =========================================================
        cursor.execute("""
            SELECT COUNT(*) AS total_departments
            FROM departments
        """)
        total_departments = cursor.fetchone()["total_departments"]

        # =========================================================
        # 3. TODAY'S PRESENT EMPLOYEES
        # =========================================================
        cursor.execute("""
            SELECT COUNT(*) AS total_present
            FROM attendance a
            JOIN employees e
                ON a.employee_id = e.employee_id
            WHERE a.attendance_date = CURDATE()
              AND a.status = 'Present'
              AND e.status = 'Active'
        """)
        total_present = cursor.fetchone()["total_present"]

        # =========================================================
        # 4. TODAY'S LATE EMPLOYEES
        # =========================================================
        cursor.execute("""
            SELECT COUNT(*) AS total_late
            FROM attendance a
            JOIN employees e
                ON a.employee_id = e.employee_id
            WHERE a.attendance_date = CURDATE()
              AND a.status = 'Late'
              AND e.status = 'Active'
        """)
        total_late = cursor.fetchone()["total_late"]

        # =========================================================
        # 5. TODAY'S ABSENT EMPLOYEES
        # =========================================================
        cursor.execute("""
            SELECT COUNT(*) AS total_absent
            FROM employees e
            LEFT JOIN attendance a
                ON e.employee_id = a.employee_id
                AND a.attendance_date = CURDATE()
            WHERE e.status = 'Active'
              AND a.attendance_id IS NULL
        """)
        total_absent = cursor.fetchone()["total_absent"]

        # =========================================================
        # 6. ACTIVE PROJECTS
        # =========================================================
        cursor.execute("""
            SELECT COUNT(*) AS active_projects
            FROM projects
            WHERE status = 'Active'
        """)
        active_projects = cursor.fetchone()["active_projects"]

        # =========================================================
        # 7. EMPLOYEES CURRENTLY WORKING
        # =========================================================
        cursor.execute("""
            SELECT COUNT(*) AS currently_working
            FROM attendance a
            JOIN employees e
                ON a.employee_id = e.employee_id
            WHERE a.attendance_date = CURDATE()
              AND a.check_in IS NOT NULL
              AND a.check_out IS NULL
              AND e.status = 'Active'
        """)
        currently_working = cursor.fetchone()["currently_working"]

        # =========================================================
        # 8. RECENT EMPLOYEES
        # =========================================================
        cursor.execute("""
            SELECT
                e.employee_code,
                e.full_name,
                d.department_name,
                e.designation,
                e.joining_date
            FROM employees e
            LEFT JOIN departments d
                ON e.department_id = d.department_id
            WHERE e.status = 'Active'
            ORDER BY e.employee_id DESC
            LIMIT 5
        """)

        recent_employees = cursor.fetchall()

        # =========================================================
        # DISPLAY DASHBOARD
        # =========================================================

        print("\n" + "=" * 70)
        print("                     ADMIN DASHBOARD")
        print("=" * 70)

        print("\n📊 COMPANY OVERVIEW")
        print("-" * 70)
        print(f"👥 Total Active Employees : {total_employees}")
        print(f"🏢 Total Departments      : {total_departments}")
        print(f"📁 Active Projects        : {active_projects}")

        print("\n🕐 TODAY'S ATTENDANCE")
        print("-" * 70)
        print(f"✅ Present                : {total_present}")
        print(f"⏰ Late                   : {total_late}")
        print(f"❌ Absent                 : {total_absent}")
        print(f"💼 Currently Working      : {currently_working}")

        print("\n👤 RECENT EMPLOYEES")
        print("-" * 70)

        if recent_employees:
            print(
                f"{'Code':<12}"
                f"{'Name':<22}"
                f"{'Department':<18}"
                f"{'Designation':<18}"
                f"{'Joining Date':<12}"
            )
            print("-" * 82)

            for employee in recent_employees:
                print(
                    f"{employee['employee_code']:<12}"
                    f"{employee['full_name'][:20]:<22}"
                    f"{str(employee['department_name'] or 'N/A')[:16]:<18}"
                    f"{employee['designation'][:16]:<18}"
                    f"{str(employee['joining_date']):<12}"
                )
        else:
            print("No active employees found.")

        print("\n" + "=" * 70)

        cursor.close()
        connection.close()

    except Exception as e:
        print(f"❌ Dashboard error: {e}")

        if connection.is_connected():
            connection.close()


# =============================================================
# TEST DASHBOARD DIRECTLY
# =============================================================

if __name__ == "__main__":
    show_dashboard()