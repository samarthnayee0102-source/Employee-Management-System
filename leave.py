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

        print(f"❌ Error finding employee: {e}")

        if connection.is_connected():
            connection.close()

        return None


# ============================================================
# EMPLOYEE - VIEW LEAVE BALANCE
# ============================================================

def view_leave_balance(employee_code):

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
                casual_leave,
                sick_leave,
                earned_leave,
                unpaid_leave
            FROM leave_balances
            WHERE employee_id = %s
        """, (employee["employee_id"],))

        balance = cursor.fetchone()

        if balance is None:

            print("\n❌ Leave balance record not found!")

            cursor.close()
            connection.close()
            return

        print("\n")
        print("=" * 65)
        print("                    LEAVE BALANCE")
        print("=" * 65)

        print(f"Employee ID : {employee['employee_code']}")
        print(f"Name        : {employee['full_name']}")
        print(f"Department  : {employee['department_name']}")

        print("-" * 65)

        print(
            f"Casual Leave       : "
            f"{balance['casual_leave']} days"
        )

        print(
            f"Sick Leave         : "
            f"{balance['sick_leave']} days"
        )

        print(
            f"Earned Leave       : "
            f"{balance['earned_leave']} days"
        )

        print(
            f"Unpaid Leave       : "
            f"{balance['unpaid_leave']} days"
        )

        print("=" * 65)

        cursor.close()
        connection.close()

    except Exception as e:

        print(f"\n❌ Error loading leave balance: {e}")

        if connection.is_connected():
            connection.close()


# ============================================================
# HELPER - GET LEAVE BALANCE COLUMN
# ============================================================

def get_leave_balance_column(leave_type):

    balance_columns = {
        "Casual Leave": "casual_leave",
        "Sick Leave": "sick_leave",
        "Earned Leave": "earned_leave",
        "Unpaid Leave": "unpaid_leave"
    }

    return balance_columns.get(leave_type)


# ============================================================
# EMPLOYEE - APPLY FOR LEAVE
# ============================================================

def apply_leave(employee_code):

    employee = get_employee_by_code(employee_code)

    if employee is None:

        print("\n❌ Employee not found!")
        return

    if employee["status"] == "Inactive":

        print("\n❌ Inactive employees cannot apply for leave!")
        return

    connection = create_connection()

    if connection is None:
        return

    try:

        cursor = connection.cursor(dictionary=True)

        # --------------------------------------------------
        # LEAVE TYPE
        # --------------------------------------------------

        print("\n")
        print("=" * 65)
        print("                    APPLY FOR LEAVE")
        print("=" * 65)

        print("1. Casual Leave")
        print("2. Sick Leave")
        print("3. Earned Leave")
        print("4. Unpaid Leave")
        print("5. Back")

        leave_choice = input("\nEnter Leave Type: ").strip()

        leave_type_map = {
            "1": "Casual Leave",
            "2": "Sick Leave",
            "3": "Earned Leave",
            "4": "Unpaid Leave"
        }

        if leave_choice == "5":
            cursor.close()
            connection.close()
            return

        if leave_choice not in leave_type_map:

            print("\n❌ Invalid leave type!")

            cursor.close()
            connection.close()
            return

        leave_type = leave_type_map[leave_choice]

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

            except ValueError:

                print(
                    "❌ Invalid date format! "
                    "Use YYYY-MM-DD."
                )

                continue

            break

        # --------------------------------------------------
        # END DATE
        # --------------------------------------------------

        while True:

            end_date_input = input(
                "Enter End Date (YYYY-MM-DD): "
            ).strip()

            try:

                end_date = datetime.strptime(
                    end_date_input,
                    "%Y-%m-%d"
                ).date()

            except ValueError:

                print(
                    "❌ Invalid date format! "
                    "Use YYYY-MM-DD."
                )

                continue

            if end_date < start_date:

                print(
                    "❌ End date cannot be before start date!"
                )

                continue

            break

        # --------------------------------------------------
        # TOTAL DAYS
        # --------------------------------------------------

        total_days = (
            end_date - start_date
        ).days + 1

        print(
            f"\nTotal Leave Days : {total_days}"
        )

        # --------------------------------------------------
        # CHECK EXISTING OVERLAPPING REQUESTS
        # --------------------------------------------------

        cursor.execute("""
            SELECT
                leave_id,
                start_date,
                end_date,
                status
            FROM leave_requests
            WHERE employee_id = %s
            AND status IN ('Pending', 'Approved')
            AND start_date <= %s
            AND end_date >= %s
            LIMIT 1
        """, (
            employee["employee_id"],
            end_date,
            start_date
        ))

        overlapping_leave = cursor.fetchone()

        if overlapping_leave is not None:

            print("\n❌ Leave dates overlap with an existing request!")

            print(
                f"Existing Leave : "
                f"{overlapping_leave['start_date']} "
                f"to "
                f"{overlapping_leave['end_date']}"
            )

            print(
                f"Status         : "
                f"{overlapping_leave['status']}"
            )

            cursor.close()
            connection.close()
            return

        # --------------------------------------------------
        # CHECK LEAVE BALANCE
        # --------------------------------------------------

        cursor.execute("""
            SELECT
                casual_leave,
                sick_leave,
                earned_leave,
                unpaid_leave
            FROM leave_balances
            WHERE employee_id = %s
        """, (employee["employee_id"],))

        balance = cursor.fetchone()

        if balance is None:

            print("\n❌ Leave balance record not found!")

            cursor.close()
            connection.close()
            return

        balance_column = get_leave_balance_column(
            leave_type
        )

        available_balance = balance[balance_column]

        # Unpaid leave can be requested without a
        # positive balance.

        if leave_type != "Unpaid Leave":

            if available_balance < total_days:

                print("\n❌ Insufficient leave balance!")

                print(
                    f"Available {leave_type}: "
                    f"{available_balance} days"
                )

                print(
                    f"Requested: {total_days} days"
                )

                cursor.close()
                connection.close()
                return

        # --------------------------------------------------
        # REASON
        # --------------------------------------------------

        while True:

            reason = input(
                "Enter Reason: "
            ).strip()

            if reason == "":

                print("❌ Reason cannot be empty!")
                continue

            if len(reason) < 3:

                print(
                    "❌ Reason must contain at least 3 characters!"
                )

                continue

            if len(reason) > 500:

                print(
                    "❌ Reason cannot exceed 500 characters!"
                )

                continue

            break

        # --------------------------------------------------
        # INSERT LEAVE REQUEST
        # --------------------------------------------------

        cursor.execute("""
            INSERT INTO leave_requests
            (
                employee_id,
                leave_type,
                start_date,
                end_date,
                reason,
                total_days,
                status
            )
            VALUES
            (%s, %s, %s, %s, %s, %s, 'Pending')
        """, (
            employee["employee_id"],
            leave_type,
            start_date,
            end_date,
            reason,
            total_days
        ))

        leave_id = cursor.lastrowid

        connection.commit()

        # --------------------------------------------------
        # DISPLAY RESULT
        # --------------------------------------------------

        print("\n")
        print("=" * 65)
        print("             ✅ LEAVE REQUEST SUBMITTED")
        print("=" * 65)

        print(f"Leave ID    : {leave_id}")
        print(f"Employee    : {employee['employee_code']}")
        print(f"Leave Type  : {leave_type}")
        print(f"Start Date  : {start_date}")
        print(f"End Date    : {end_date}")
        print(f"Total Days  : {total_days}")
        print(f"Reason      : {reason}")
        print("Status      : Pending")

        print("=" * 65)

        cursor.close()
        connection.close()

    except Exception as e:

        connection.rollback()

        print(
            f"\n❌ Error applying for leave: {e}"
        )

        if connection.is_connected():
            connection.close()


# ============================================================
# EMPLOYEE - VIEW OWN LEAVE REQUESTS
# ============================================================

def view_my_leave_requests(employee_code):

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
                leave_id,
                leave_type,
                start_date,
                end_date,
                total_days,
                reason,
                status,
                admin_remark,
                applied_at,
                reviewed_at
            FROM leave_requests
            WHERE employee_id = %s
            ORDER BY applied_at DESC
        """, (employee["employee_id"],))

        requests = cursor.fetchall()

        print("\n")
        print("=" * 120)
        print(" " * 45 + "MY LEAVE REQUESTS")
        print("=" * 120)

        print(
            f"Employee ID : {employee['employee_code']}"
        )

        print(
            f"Name        : {employee['full_name']}"
        )

        print("-" * 120)

        if not requests:

            print("\n❌ No leave requests found.")

            print("=" * 120)

            cursor.close()
            connection.close()
            return

        print(
            f"{'ID':<8}"
            f"{'TYPE':<18}"
            f"{'START':<13}"
            f"{'END':<13}"
            f"{'DAYS':<8}"
            f"{'STATUS':<13}"
            f"{'REMARK':<40}"
        )

        print("-" * 120)

        for request in requests:

            remark = request["admin_remark"]

            if remark is None or str(remark).strip() == "":
                remark = "--"
            else:
                remark = str(remark)

            if len(remark) > 37:
                remark = remark[:34] + "..."

            print(
                f"{request['leave_id']:<8}"
                f"{request['leave_type']:<18}"
                f"{str(request['start_date']):<13}"
                f"{str(request['end_date']):<13}"
                f"{request['total_days']:<8}"
                f"{request['status']:<13}"
                f"{remark:<40}"
            )

        print("-" * 120)

        cursor.close()
        connection.close()

    except Exception as e:

        print(
            f"\n❌ Error loading leave requests: {e}"
        )

        if connection.is_connected():
            connection.close()


# ============================================================
# ADMIN - VIEW PENDING LEAVE REQUESTS
# ============================================================

def view_pending_leave_requests():

    connection = create_connection()

    if connection is None:
        return

    try:

        cursor = connection.cursor(dictionary=True)

        cursor.execute("""
            SELECT
                lr.leave_id,
                e.employee_code,
                e.full_name,
                d.department_name,
                lr.leave_type,
                lr.start_date,
                lr.end_date,
                lr.total_days,
                lr.reason,
                lr.applied_at
            FROM leave_requests lr
            INNER JOIN employees e
                ON lr.employee_id = e.employee_id
            INNER JOIN departments d
                ON e.department_id = d.department_id
            WHERE lr.status = 'Pending'
            ORDER BY lr.applied_at ASC
        """)

        requests = cursor.fetchall()

        print("\n")
        print("=" * 120)
        print(" " * 42 + "PENDING LEAVE REQUESTS")
        print("=" * 120)

        if not requests:

            print("\n✅ No pending leave requests.")

            print("=" * 120)

            cursor.close()
            connection.close()
            return

        print(
            f"{'ID':<8}"
            f"{'EMP ID':<10}"
            f"{'NAME':<22}"
            f"{'TYPE':<18}"
            f"{'START':<13}"
            f"{'END':<13}"
            f"{'DAYS':<8}"
        )

        print("-" * 120)

        for request in requests:

            print(
                f"{request['leave_id']:<8}"
                f"{request['employee_code']:<10}"
                f"{request['full_name']:<22}"
                f"{request['leave_type']:<18}"
                f"{str(request['start_date']):<13}"
                f"{str(request['end_date']):<13}"
                f"{request['total_days']:<8}"
            )

        print("-" * 120)

        cursor.close()
        connection.close()

    except Exception as e:

        print(
            f"\n❌ Error loading pending requests: {e}"
        )

        if connection.is_connected():
            connection.close()


# ============================================================
# ADMIN - VIEW ALL LEAVE REQUESTS
# ============================================================

def view_all_leave_requests():

    connection = create_connection()

    if connection is None:
        return

    try:

        cursor = connection.cursor(dictionary=True)

        cursor.execute("""
            SELECT
                lr.leave_id,
                e.employee_code,
                e.full_name,
                d.department_name,
                lr.leave_type,
                lr.start_date,
                lr.end_date,
                lr.total_days,
                lr.status,
                lr.reason,
                lr.admin_remark,
                lr.applied_at,
                lr.reviewed_at
            FROM leave_requests lr
            INNER JOIN employees e
                ON lr.employee_id = e.employee_id
            INNER JOIN departments d
                ON e.department_id = d.department_id
            ORDER BY lr.applied_at DESC
        """)

        requests = cursor.fetchall()

        print("\n")
        print("=" * 135)
        print(" " * 50 + "ALL LEAVE REQUESTS")
        print("=" * 135)

        if not requests:

            print("\n❌ No leave requests found.")

            print("=" * 135)

            cursor.close()
            connection.close()
            return

        print(
            f"{'ID':<7}"
            f"{'EMP ID':<10}"
            f"{'NAME':<20}"
            f"{'TYPE':<17}"
            f"{'START':<12}"
            f"{'END':<12}"
            f"{'DAYS':<7}"
            f"{'STATUS':<12}"
            f"{'REMARK':<35}"
        )

        print("-" * 135)

        for request in requests:

            remark = request["admin_remark"]

            if remark is None or str(remark).strip() == "":
                remark = "--"
            else:
                remark = str(remark)

            if len(remark) > 32:
                remark = remark[:29] + "..."

            print(
                f"{request['leave_id']:<7}"
                f"{request['employee_code']:<10}"
                f"{request['full_name']:<20}"
                f"{request['leave_type']:<17}"
                f"{str(request['start_date']):<12}"
                f"{str(request['end_date']):<12}"
                f"{request['total_days']:<7}"
                f"{request['status']:<12}"
                f"{remark:<35}"
            )

        print("-" * 135)

        cursor.close()
        connection.close()

    except Exception as e:

        print(
            f"\n❌ Error loading leave requests: {e}"
        )

        if connection.is_connected():
            connection.close()


# ============================================================
# ADMIN - VIEW LEAVE REQUEST DETAILS
# ============================================================

def view_leave_request_details():

    connection = create_connection()

    if connection is None:
        return

    try:

        cursor = connection.cursor(dictionary=True)

        print("\n")
        print("=" * 65)
        print("              LEAVE REQUEST DETAILS")
        print("=" * 65)

        leave_id_input = input(
            "Enter Leave ID: "
        ).strip()

        if not leave_id_input.isdigit():

            print("\n❌ Leave ID must be a number!")

            cursor.close()
            connection.close()
            return

        leave_id = int(leave_id_input)

        cursor.execute("""
            SELECT
                lr.leave_id,
                e.employee_code,
                e.full_name,
                e.email,
                d.department_name,
                e.designation,
                lr.leave_type,
                lr.start_date,
                lr.end_date,
                lr.total_days,
                lr.reason,
                lr.status,
                lr.admin_remark,
                lr.applied_at,
                lr.reviewed_at
            FROM leave_requests lr
            INNER JOIN employees e
                ON lr.employee_id = e.employee_id
            INNER JOIN departments d
                ON e.department_id = d.department_id
            WHERE lr.leave_id = %s
        """, (leave_id,))

        request = cursor.fetchone()

        if request is None:

            print("\n❌ Leave request not found!")

            cursor.close()
            connection.close()
            return

        print("\n")
        print("=" * 65)
        print("              LEAVE REQUEST DETAILS")
        print("=" * 65)

        print(f"Leave ID       : {request['leave_id']}")
        print(f"Employee ID    : {request['employee_code']}")
        print(f"Employee Name  : {request['full_name']}")
        print(f"Email          : {request['email']}")
        print(f"Department     : {request['department_name']}")
        print(f"Designation    : {request['designation']}")

        print("-" * 65)

        print(f"Leave Type     : {request['leave_type']}")
        print(f"Start Date     : {request['start_date']}")
        print(f"End Date       : {request['end_date']}")
        print(f"Total Days     : {request['total_days']}")
        print(f"Reason         : {request['reason']}")
        print(f"Status         : {request['status']}")

        if request["admin_remark"]:
            print(
                f"Admin Remark   : "
                f"{request['admin_remark']}"
            )
        else:
            print("Admin Remark   : --")

        print(f"Applied At     : {request['applied_at']}")

        if request["reviewed_at"]:
            print(
                f"Reviewed At    : "
                f"{request['reviewed_at']}"
            )
        else:
            print("Reviewed At    : --")

        print("=" * 65)

        cursor.close()
        connection.close()

    except Exception as e:

        print(
            f"\n❌ Error loading request details: {e}"
        )

        if connection.is_connected():
            connection.close()


# ============================================================
# ADMIN - APPROVE LEAVE
# ============================================================

def approve_leave():

    connection = create_connection()

    if connection is None:
        return

    try:

        cursor = connection.cursor(dictionary=True)

        print("\n")
        print("=" * 65)
        print("                 APPROVE LEAVE")
        print("=" * 65)

        leave_id_input = input(
            "Enter Leave ID: "
        ).strip()

        if not leave_id_input.isdigit():

            print("\n❌ Leave ID must be a number!")

            cursor.close()
            connection.close()
            return

        leave_id = int(leave_id_input)

        # --------------------------------------------------
        # GET REQUEST
        # --------------------------------------------------

        cursor.execute("""
            SELECT
                lr.*,
                e.employee_code,
                e.full_name
            FROM leave_requests lr
            INNER JOIN employees e
                ON lr.employee_id = e.employee_id
            WHERE lr.leave_id = %s
        """, (leave_id,))

        request = cursor.fetchone()

        if request is None:

            print("\n❌ Leave request not found!")

            cursor.close()
            connection.close()
            return

        if request["status"] != "Pending":

            print(
                f"\n❌ This leave request is already "
                f"{request['status']}."
            )

            cursor.close()
            connection.close()
            return

        # --------------------------------------------------
        # CHECK BALANCE AGAIN
        # --------------------------------------------------

        balance_column = get_leave_balance_column(
            request["leave_type"]
        )

        cursor.execute(f"""
            SELECT {balance_column}
            FROM leave_balances
            WHERE employee_id = %s
            FOR UPDATE
        """, (request["employee_id"],))

        balance = cursor.fetchone()

        if balance is None:

            print("\n❌ Leave balance record not found!")

            connection.rollback()
            cursor.close()
            connection.close()
            return

        available_balance = balance[balance_column]

        # Unpaid leave does not require balance.

        if request["leave_type"] != "Unpaid Leave":

            if available_balance < request["total_days"]:

                print("\n❌ Insufficient leave balance!")

                print(
                    f"Available : {available_balance} days"
                )

                print(
                    f"Required  : "
                    f"{request['total_days']} days"
                )

                connection.rollback()

                cursor.close()
                connection.close()
                return

        # --------------------------------------------------
        # CHECK FOR ANOTHER APPROVED OVERLAPPING REQUEST
        # --------------------------------------------------

        cursor.execute("""
            SELECT leave_id
            FROM leave_requests
            WHERE employee_id = %s
            AND leave_id != %s
            AND status = 'Approved'
            AND start_date <= %s
            AND end_date >= %s
            LIMIT 1
        """, (
            request["employee_id"],
            request["leave_id"],
            request["end_date"],
            request["start_date"]
        ))

        overlapping_request = cursor.fetchone()

        if overlapping_request is not None:

            print(
                "\n❌ Another approved leave overlaps "
                "with these dates!"
            )

            connection.rollback()

            cursor.close()
            connection.close()
            return

        # --------------------------------------------------
        # ADMIN REMARK
        # --------------------------------------------------

        admin_remark = input(
            "Enter Admin Remark: "
        ).strip()

        if len(admin_remark) > 500:

            print(
                "\n❌ Admin remark cannot exceed "
                "500 characters!"
            )

            connection.rollback()

            cursor.close()
            connection.close()
            return

        # --------------------------------------------------
        # UPDATE REQUEST
        # --------------------------------------------------

        cursor.execute("""
            UPDATE leave_requests
            SET
                status = 'Approved',
                admin_remark = %s,
                reviewed_at = CURRENT_TIMESTAMP
            WHERE leave_id = %s
            AND status = 'Pending'
        """, (
            admin_remark,
            leave_id
        ))

        # --------------------------------------------------
        # DEDUCT BALANCE
        # --------------------------------------------------

        if request["leave_type"] != "Unpaid Leave":

            cursor.execute(f"""
                UPDATE leave_balances
                SET {balance_column} =
                    {balance_column} - %s
                WHERE employee_id = %s
            """, (
                request["total_days"],
                request["employee_id"]
            ))

        connection.commit()

        print("\n")
        print("=" * 65)
        print("             ✅ LEAVE APPROVED")
        print("=" * 65)

        print(f"Leave ID    : {leave_id}")
        print(
            f"Employee    : "
            f"{request['employee_code']} - "
            f"{request['full_name']}"
        )
        print(
            f"Leave Type  : "
            f"{request['leave_type']}"
        )
        print(
            f"Dates       : "
            f"{request['start_date']} "
            f"to "
            f"{request['end_date']}"
        )
        print(
            f"Total Days  : "
            f"{request['total_days']}"
        )
        print("Status      : Approved")

        print("=" * 65)

        cursor.close()
        connection.close()

    except Exception as e:

        connection.rollback()

        print(
            f"\n❌ Error approving leave: {e}"
        )

        if connection.is_connected():
            connection.close()


# ============================================================
# ADMIN - REJECT LEAVE
# ============================================================

def reject_leave():

    connection = create_connection()

    if connection is None:
        return

    try:

        cursor = connection.cursor(dictionary=True)

        print("\n")
        print("=" * 65)
        print("                  REJECT LEAVE")
        print("=" * 65)

        leave_id_input = input(
            "Enter Leave ID: "
        ).strip()

        if not leave_id_input.isdigit():

            print("\n❌ Leave ID must be a number!")

            cursor.close()
            connection.close()
            return

        leave_id = int(leave_id_input)

        # --------------------------------------------------
        # GET REQUEST
        # --------------------------------------------------

        cursor.execute("""
            SELECT
                lr.*,
                e.employee_code,
                e.full_name
            FROM leave_requests lr
            INNER JOIN employees e
                ON lr.employee_id = e.employee_id
            WHERE lr.leave_id = %s
        """, (leave_id,))

        request = cursor.fetchone()

        if request is None:

            print("\n❌ Leave request not found!")

            cursor.close()
            connection.close()
            return

        if request["status"] != "Pending":

            print(
                f"\n❌ This leave request is already "
                f"{request['status']}."
            )

            cursor.close()
            connection.close()
            return

        # --------------------------------------------------
        # ADMIN REMARK
        # --------------------------------------------------

        while True:

            admin_remark = input(
                "Enter Reason for Rejection: "
            ).strip()

            if admin_remark == "":

                print(
                    "❌ Rejection reason cannot be empty!"
                )

                continue

            if len(admin_remark) > 500:

                print(
                    "❌ Rejection reason cannot "
                    "exceed 500 characters!"
                )

                continue

            break

        # --------------------------------------------------
        # UPDATE REQUEST
        # --------------------------------------------------

        cursor.execute("""
            UPDATE leave_requests
            SET
                status = 'Rejected',
                admin_remark = %s,
                reviewed_at = CURRENT_TIMESTAMP
            WHERE leave_id = %s
            AND status = 'Pending'
        """, (
            admin_remark,
            leave_id
        ))

        connection.commit()

        print("\n")
        print("=" * 65)
        print("             ❌ LEAVE REJECTED")
        print("=" * 65)

        print(f"Leave ID    : {leave_id}")
        print(
            f"Employee    : "
            f"{request['employee_code']} - "
            f"{request['full_name']}"
        )
        print(
            f"Leave Type  : "
            f"{request['leave_type']}"
        )
        print(
            f"Dates       : "
            f"{request['start_date']} "
            f"to "
            f"{request['end_date']}"
        )
        print(
            f"Total Days  : "
            f"{request['total_days']}"
        )
        print("Status      : Rejected")
        print(
            f"Admin Remark: "
            f"{admin_remark}"
        )

        print("=" * 65)

        cursor.close()
        connection.close()

    except Exception as e:

        connection.rollback()

        print(
            f"\n❌ Error rejecting leave: {e}"
        )

        if connection.is_connected():
            connection.close()



