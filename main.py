from authentication import login

from employee import (
    add_employee,
    view_all_employees,
    search_employee,
    update_employee,
    delete_employee,
    view_employee_details
)

from attendance import (
    check_in,
    check_out,
    view_today_attendance,
    view_employee_attendance
)

from leave import (
    view_leave_balance,
    apply_leave,
    view_my_leave_requests,
    view_pending_leave_requests,
    view_all_leave_requests,
    view_leave_request_details,
    approve_leave,
    reject_leave
)

from project import (
    add_project,
    view_all_projects,
    search_project,
    view_project_details,
    update_project,
    assign_employee_to_project,
    view_project_employees,
    view_my_projects,
    remove_employee_from_project,
    complete_employee_assignment
)

from notification import (
    notification_menu,
    count_unread_notifications
)

from activity_log import (
    activity_log_menu,
    create_activity_log
)

from report import (
    report_menu
)

from dashboard import (
    show_dashboard
)

from database import create_connection


# ============================================================
# UTILITY FUNCTIONS
# ============================================================

def clear_screen():
    print("\n" * 3)


def pause():
    input("\nPress Enter to continue...")


# ============================================================
# GET EMPLOYEE CODE FROM LOGGED-IN USER
# ============================================================

def get_employee_code(user):

    if user.get("employee_id") is None:
        print("❌ No employee account is linked to this user.")
        return None

    connection = create_connection()

    if connection is None:
        return None

    try:
        cursor = connection.cursor()

        cursor.execute("""
            SELECT employee_code
            FROM employees
            WHERE employee_id = %s
        """, (user["employee_id"],))

        result = cursor.fetchone()

        cursor.close()
        connection.close()

        if result is None:
            print("❌ Employee record not found.")
            return None

        return result[0]

    except Exception as e:

        print(f"❌ Error loading employee information: {e}")

        if connection.is_connected():
            connection.close()

        return None


# ============================================================
# CREATE LOG HELPER
# ============================================================

def log_action(user, action, description):

    if user is None:
        return

    user_id = user.get("user_id")

    if user_id is None:
        return

    create_activity_log(
        user_id,
        action,
        description
    )


# ============================================================
# VIEW MY PROFILE
# ============================================================

def view_my_profile(user):

    employee_code = get_employee_code(user)

    if employee_code is None:
        return

    connection = create_connection()

    if connection is None:
        return

    try:

        cursor = connection.cursor(dictionary=True)

        query = """
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
            WHERE e.employee_id = %s
        """

        cursor.execute(query, (user["employee_id"],))

        employee = cursor.fetchone()

        cursor.close()
        connection.close()

        if employee is None:
            print("❌ Employee profile not found!")
            return

        print("\n")
        print("╔" + "═" * 53 + "╗")
        print("║" + " MY PROFILE ".center(53) + "║")
        print("╠" + "═" * 53 + "╣")

        print(f"║ Employee ID    : {employee['employee_code']:<34}║")
        print(f"║ Name           : {employee['full_name']:<34}║")
        print(f"║ Email          : {employee['email']:<34}║")
        print(f"║ Phone          : {employee['phone']:<34}║")
        print(f"║ Department     : {employee['department_name']:<34}║")
        print(f"║ Designation    : {employee['designation']:<34}║")
        print(f"║ Salary         : ₹{employee['salary']:<33.2f}║")
        print(f"║ Date of Birth  : {str(employee['date_of_birth']):<34}║")
        print(f"║ Joining Date   : {str(employee['joining_date']):<34}║")
        print(f"║ Status         : {employee['status']:<34}║")

        print("╚" + "═" * 53 + "╝")

    except Exception as e:

        print(f"❌ Error loading profile: {e}")

        if connection.is_connected():
            connection.close()


# ============================================================
# EMPLOYEE MANAGEMENT MENU
# ============================================================

def employee_management_menu(user):

    while True:

        clear_screen()

        print("=" * 60)
        print("              EMPLOYEE MANAGEMENT")
        print("=" * 60)

        print("1. Add Employee")
        print("2. View All Employees")
        print("3. Search Employee")
        print("4. Update Employee")
        print("5. Delete Employee")
        print("6. View Employee Details")
        print("7. Back")

        print("=" * 60)

        choice = input("Enter your choice: ").strip()

        if choice == "1":

            clear_screen()
            add_employee()

            log_action(
                user,
                "ADD EMPLOYEE",
                "Admin added a new employee."
            )

            pause()

        elif choice == "2":

            clear_screen()
            view_all_employees()
            pause()

        elif choice == "3":

            clear_screen()
            search_employee()
            pause()

        elif choice == "4":

            clear_screen()
            update_employee()

            log_action(
                user,
                "UPDATE EMPLOYEE",
                "Admin updated employee information."
            )

            pause()

        elif choice == "5":

            clear_screen()
            delete_employee()

            log_action(
                user,
                "DELETE EMPLOYEE",
                "Admin deleted an employee."
            )

            pause()

        elif choice == "6":

            clear_screen()
            view_employee_details()
            pause()

        elif choice == "7":

            break

        else:

            print("\n❌ Invalid choice!")
            pause()


# ============================================================
# ADMIN ATTENDANCE MENU
# ============================================================

def admin_attendance_menu():

    while True:

        clear_screen()

        print("=" * 60)
        print("                 ATTENDANCE MANAGEMENT")
        print("=" * 60)

        print("1. View Today's Attendance")
        print("2. View Employee Attendance")
        print("3. Back")

        print("=" * 60)

        choice = input("Enter your choice: ").strip()

        if choice == "1":

            clear_screen()
            view_today_attendance()
            pause()

        elif choice == "2":

            clear_screen()
            view_employee_attendance()
            pause()

        elif choice == "3":

            break

        else:

            print("\n❌ Invalid choice!")
            pause()


# ============================================================
# EMPLOYEE ATTENDANCE MENU
# ============================================================

def employee_attendance_menu(user):

    employee_code = get_employee_code(user)

    if employee_code is None:
        pause()
        return

    while True:

        clear_screen()

        print("=" * 60)
        print("                     MY ATTENDANCE")
        print("=" * 60)

        print("1. Check-In")
        print("2. Check-Out")
        print("3. Back")

        print("=" * 60)

        choice = input("Enter your choice: ").strip()

        if choice == "1":

            clear_screen()
            check_in(employee_code)

            log_action(
                user,
                "CHECK IN",
                f"{employee_code} performed attendance check-in."
            )

            pause()

        elif choice == "2":

            clear_screen()
            check_out(employee_code)

            log_action(
                user,
                "CHECK OUT",
                f"{employee_code} performed attendance check-out."
            )

            pause()

        elif choice == "3":

            break

        else:

            print("\n❌ Invalid choice!")
            pause()


# ============================================================
# ADMIN LEAVE MENU
# ============================================================

def admin_leave_menu(user):

    while True:

        clear_screen()

        print("=" * 60)
        print("                   LEAVE MANAGEMENT")
        print("=" * 60)

        print("1. View Pending Leave Requests")
        print("2. View All Leave Requests")
        print("3. View Leave Request Details")
        print("4. Approve Leave")
        print("5. Reject Leave")
        print("6. Back")

        print("=" * 60)

        choice = input("Enter your choice: ").strip()

        if choice == "1":

            clear_screen()
            view_pending_leave_requests()
            pause()

        elif choice == "2":

            clear_screen()
            view_all_leave_requests()
            pause()

        elif choice == "3":

            clear_screen()
            view_leave_request_details()
            pause()

        elif choice == "4":

            clear_screen()
            approve_leave()

            log_action(
                user,
                "APPROVE LEAVE",
                "Admin approved a leave request."
            )

            pause()

        elif choice == "5":

            clear_screen()
            reject_leave()

            log_action(
                user,
                "REJECT LEAVE",
                "Admin rejected a leave request."
            )

            pause()

        elif choice == "6":

            break

        else:

            print("\n❌ Invalid choice!")
            pause()


# ============================================================
# EMPLOYEE LEAVE MENU
# ============================================================

def employee_leave_menu(user):

    employee_code = get_employee_code(user)

    if employee_code is None:
        pause()
        return

    while True:

        clear_screen()

        print("=" * 60)
        print("                    MY LEAVE")
        print("=" * 60)

        print("1. View Leave Balance")
        print("2. Apply for Leave")
        print("3. View My Leave Requests")
        print("4. View Leave Request Details")
        print("5. Back")

        print("=" * 60)

        choice = input("Enter your choice: ").strip()

        if choice == "1":

            clear_screen()
            view_leave_balance(employee_code)
            pause()

        elif choice == "2":

            clear_screen()
            apply_leave(employee_code)

            log_action(
                user,
                "APPLY LEAVE",
                f"{employee_code} submitted a leave request."
            )

            pause()

        elif choice == "3":

            clear_screen()
            view_my_leave_requests(employee_code)
            pause()

        elif choice == "4":

            clear_screen()
            view_leave_request_details()
            pause()

        elif choice == "5":

            break

        else:

            print("\n❌ Invalid choice!")
            pause()


# ============================================================
# ADMIN PROJECT MENU
# ============================================================

def admin_project_menu(user):

    while True:

        clear_screen()

        print("=" * 60)
        print("                  PROJECT MANAGEMENT")
        print("=" * 60)

        print("1. Add Project")
        print("2. View All Projects")
        print("3. Search Project")
        print("4. View Project Details")
        print("5. Update Project")
        print("6. Assign Employee")
        print("7. View Project Employees")
        print("8. Remove Employee From Project")
        print("9. Complete Employee Assignment")
        print("10. Back")

        print("=" * 60)

        choice = input("Enter your choice: ").strip()

        if choice == "1":

            clear_screen()
            add_project()

            log_action(
                user,
                "ADD PROJECT",
                "Admin created a new project."
            )

            pause()

        elif choice == "2":

            clear_screen()
            view_all_projects()
            pause()

        elif choice == "3":

            clear_screen()
            search_project()
            pause()

        elif choice == "4":

            clear_screen()
            view_project_details()
            pause()

        elif choice == "5":

            clear_screen()
            update_project()

            log_action(
                user,
                "UPDATE PROJECT",
                "Admin updated project information."
            )

            pause()

        elif choice == "6":

            clear_screen()
            assign_employee_to_project()

            log_action(
                user,
                "ASSIGN PROJECT",
                "Admin assigned an employee to a project."
            )

            pause()

        elif choice == "7":

            clear_screen()
            view_project_employees()
            pause()

        elif choice == "8":

            clear_screen()
            remove_employee_from_project()

            log_action(
                user,
                "REMOVE PROJECT ASSIGNMENT",
                "Admin removed an employee from a project."
            )

            pause()

        elif choice == "9":

            clear_screen()
            complete_employee_assignment()

            log_action(
                user,
                "COMPLETE PROJECT ASSIGNMENT",
                "Admin completed an employee project assignment."
            )

            pause()

        elif choice == "10":

            break

        else:

            print("\n❌ Invalid choice!")
            pause()


# ============================================================
# EMPLOYEE PROJECT MENU
# ============================================================

def employee_project_menu(user):

    employee_code = get_employee_code(user)

    if employee_code is None:
        pause()
        return

    clear_screen()

    print("=" * 70)
    print("                       MY PROJECTS")
    print("=" * 70)

    view_my_projects(employee_code)

    pause()


# ============================================================
# ADMIN MENU
# ============================================================

def admin_menu(user):

    while True:

        clear_screen()

        unread = count_unread_notifications(user["user_id"])

        print("=" * 65)
        print("              EMPLOYEE MANAGEMENT SYSTEM")
        print("=" * 65)
        print("                         ADMIN PANEL")
        print("=" * 65)

        print("1.  Dashboard")
        print("2.  Employee Management")
        print("3.  Attendance Management")
        print("4.  Leave Management")
        print("5.  Project Management")
        print(f"6.  Notifications ({unread} unread)")
        print("7.  Reports")
        print("8.  Activity Logs")
        print("9.  Logout")

        print("=" * 65)

        choice = input("Enter your choice: ").strip()

        if choice == "1":

            clear_screen()
            show_dashboard()
            pause()

        elif choice == "2":

            employee_management_menu(user)

        elif choice == "3":

            admin_attendance_menu()

        elif choice == "4":

            admin_leave_menu(user)

        elif choice == "5":

            admin_project_menu(user)

        elif choice == "6":

            clear_screen()
            notification_menu(user["user_id"])
            pause()

        elif choice == "7":

            clear_screen()
            report_menu()

        elif choice == "8":

            clear_screen()
            activity_log_menu()

        elif choice == "9":

            log_action(
                user,
                "LOGOUT",
                "Admin logged out of the system."
            )

            print("\n✅ Logged out successfully.")
            pause()
            break

        else:

            print("\n❌ Invalid choice!")
            pause()


# ============================================================
# EMPLOYEE MENU
# ============================================================

def employee_menu(user):

    while True:

        clear_screen()

        unread = count_unread_notifications(user["user_id"])

        print("=" * 65)
        print("              EMPLOYEE MANAGEMENT SYSTEM")
        print("=" * 65)
        print("                    EMPLOYEE PORTAL")
        print("=" * 65)

        print("1. My Profile")
        print("2. My Attendance")
        print("3. My Leave")
        print("4. My Projects")
        print(f"5. Notifications ({unread} unread)")
        print("6. My Activity")
        print("7. Logout")

        print("=" * 65)

        choice = input("Enter your choice: ").strip()

        if choice == "1":

            clear_screen()
            view_my_profile(user)
            pause()

        elif choice == "2":

            employee_attendance_menu(user)

        elif choice == "3":

            employee_leave_menu(user)

        elif choice == "4":

            employee_project_menu(user)

        elif choice == "5":

            clear_screen()
            notification_menu(user["user_id"])
            pause()

        elif choice == "6":

            clear_screen()

            from activity_log import view_my_activity_logs

            view_my_activity_logs(user["user_id"])

            pause()

        elif choice == "7":

            log_action(
                user,
                "LOGOUT",
                "Employee logged out of the system."
            )

            print("\n✅ Logged out successfully.")
            pause()
            break

        else:

            print("\n❌ Invalid choice!")
            pause()


# ============================================================
# LOGIN / START APPLICATION
# ============================================================

def start_application():

    while True:

        clear_screen()

        print("=" * 60)
        print("          EMPLOYEE MANAGEMENT SYSTEM")
        print("=" * 60)

        print("1. Login")
        print("2. Exit")

        print("=" * 60)

        choice = input("Enter your choice: ").strip()

        # ----------------------------------------------------
        # LOGIN
        # ----------------------------------------------------

        if choice == "1":

            clear_screen()

            print("=" * 60)
            print("                       LOGIN")
            print("=" * 60)

            username = input("Username: ").strip()
            password = input("Password: ").strip()

            if username == "" or password == "":
                print("\n❌ Username and password cannot be empty!")
                pause()
                continue

            user = login(username, password)

            if user is None:
                pause()
                continue

            log_action(
                user,
                "LOGIN",
                f"{username} logged into the system."
            )

            pause()

            if user["role"] == "Admin":

                admin_menu(user)

            elif user["role"] == "Employee":

                employee_menu(user)

            else:

                print("❌ Unknown user role!")
                pause()

        # ----------------------------------------------------
        # EXIT
        # ----------------------------------------------------

        elif choice == "2":

            clear_screen()

            print("=" * 60)
            print("     Thank you for using Employee Management System!")
            print("=" * 60)

            break

        else:

            print("\n❌ Invalid choice!")
            pause()


# ============================================================
# PROGRAM START
# ============================================================

if __name__ == "__main__":
    start_application()