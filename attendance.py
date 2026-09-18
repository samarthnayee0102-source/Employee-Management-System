from datetime import datetime, timedelta
from database import create_connection


def check_in(employee_code):

    connection = create_connection()

    if connection is None:
        return

    try:
        cursor = connection.cursor(dictionary=True)

        # --------------------------------------------------
        # 1. CHECK EMPLOYEE
        # --------------------------------------------------

        cursor.execute("""
            SELECT employee_id, employee_code, full_name, status
            FROM employees
            WHERE employee_code = %s
        """, (employee_code,))

        employee = cursor.fetchone()

        if employee is None:
            print("❌ Employee not found!")
            cursor.close()
            connection.close()
            return

        # --------------------------------------------------
        # 2. CHECK EMPLOYEE STATUS
        # --------------------------------------------------

        if employee["status"] != "Active":
            print("❌ Only active employees can check in!")
            cursor.close()
            connection.close()
            return

        today = datetime.now().date()
        current_time = datetime.now().time()

        # --------------------------------------------------
        # 3. CHECK APPROVED LEAVE
        # --------------------------------------------------

        cursor.execute("""
            SELECT leave_id
            FROM leave_requests
            WHERE employee_id = %s
            AND status = 'Approved'
            AND %s BETWEEN start_date AND end_date
            LIMIT 1
        """, (
            employee["employee_id"],
            today
        ))

        approved_leave = cursor.fetchone()

        if approved_leave is not None:

            print("\n" + "=" * 50)
            print("          ❌ CHECK-IN NOT ALLOWED")
            print("=" * 50)

            print("Employee is on approved leave today.")
            print("Please contact the administrator if this is incorrect.")

            print("=" * 50)

            cursor.close()
            connection.close()
            return

        # --------------------------------------------------
        # 4. CHECK EXISTING ATTENDANCE
        # --------------------------------------------------

        cursor.execute("""
            SELECT attendance_id, check_in, check_out
            FROM attendance
            WHERE employee_id = %s
            AND attendance_date = %s
        """, (
            employee["employee_id"],
            today
        ))

        attendance = cursor.fetchone()

        if attendance is not None:

            if attendance["check_in"] is not None:
                print("❌ You have already checked in today!")

            cursor.close()
            connection.close()
            return

        # --------------------------------------------------
        # 5. DETERMINE PRESENT / LATE
        # --------------------------------------------------

        reporting_time = datetime.strptime(
            "09:30:00",
            "%H:%M:%S"
        ).time()

        if current_time > reporting_time:
            attendance_status = "Late"
        else:
            attendance_status = "Present"

        # --------------------------------------------------
        # 6. INSERT ATTENDANCE
        # --------------------------------------------------

        cursor.execute("""
            INSERT INTO attendance
            (
                employee_id,
                attendance_date,
                check_in,
                status
            )
            VALUES (%s, %s, %s, %s)
        """, (
            employee["employee_id"],
            today,
            current_time,
            attendance_status
        ))

        connection.commit()

        # --------------------------------------------------
        # 7. DISPLAY RESULT
        # --------------------------------------------------

        print("\n" + "=" * 55)

        if attendance_status == "Late":
            print("             ⚠️ LATE CHECK-IN")
        else:
            print("          ✅ CHECK-IN SUCCESSFUL")

        print("=" * 55)

        print(f"Employee ID : {employee['employee_code']}")
        print(f"Employee    : {employee['full_name']}")
        print(f"Date        : {today}")
        print(f"Login Time  : {current_time}")
        print(f"Reporting   : {reporting_time}")
        print(f"Status      : {attendance_status}")

        print("=" * 55)

        if attendance_status == "Late":
            print("⚠️ You arrived after the reporting time.")

        cursor.close()
        connection.close()

    except Exception as e:

        connection.rollback()

        print(f"❌ Check-in error: {e}")

        if connection.is_connected():
            connection.close()




def check_out(employee_code):

    connection = create_connection()

    if connection is None:
        return

    try:
        cursor = connection.cursor(dictionary=True)

        # Check employee
        cursor.execute("""
            SELECT employee_id, employee_code, full_name, status
            FROM employees
            WHERE employee_code = %s
        """, (employee_code,))

        employee = cursor.fetchone()

        if employee is None:
            print("❌ Employee not found!")
            cursor.close()
            connection.close()
            return

        today = datetime.now().date()
        current_time = datetime.now().time()

        # Get today's attendance
        cursor.execute("""
            SELECT attendance_id, check_in, check_out
            FROM attendance
            WHERE employee_id = %s
            AND attendance_date = %s
        """, (
            employee["employee_id"],
            today
        ))

        attendance = cursor.fetchone()

        # No attendance record
        if attendance is None:
            print("❌ You have not checked in today!")

            cursor.close()
            connection.close()
            return

        # Already checked out
        if attendance["check_out"] is not None:
            print("❌ You have already checked out today!")

            cursor.close()
            connection.close()
            return

        # Check-in must exist
        if attendance["check_in"] is None:
            print("❌ Check-in record not found!")

            cursor.close()
            connection.close()
            return

        # Convert times to datetime objects
        check_in_value = attendance["check_in"]

        if isinstance(check_in_value, timedelta):

            total_seconds = int(check_in_value.total_seconds())

            check_in_hours = total_seconds // 3600
            check_in_minutes = (total_seconds % 3600) // 60
            check_in_seconds = total_seconds % 60

            check_in_time = datetime.strptime(
                f"{check_in_hours:02d}:{check_in_minutes:02d}:{check_in_seconds:02d}",
                "%H:%M:%S"
            ).time()

        else:
            check_in_time = check_in_value


        check_in_datetime = datetime.combine(
            today,
            check_in_time
        )

        check_out_datetime = datetime.combine(
            today,
            current_time
        )
        # Prevent checkout before check-in
        if check_out_datetime <= check_in_datetime:
            print("❌ Check-out time cannot be before check-in time!")

            cursor.close()
            connection.close()
            return

        # Calculate working hours
        working_seconds = (
            check_out_datetime - check_in_datetime
        ).total_seconds()

        working_hours = working_seconds / 3600

        # Update attendance
        cursor.execute("""
            UPDATE attendance
            SET
                check_out = %s,
                working_hours = %s
            WHERE attendance_id = %s
        """, (
            current_time,
            working_hours,
            attendance["attendance_id"]
        ))

        connection.commit()

        # Display result
        total_seconds = int(working_seconds)

        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60

        print("\n" + "=" * 55)
        print("           ✅ CHECK-OUT SUCCESSFUL")
        print("=" * 55)

        print(f"Employee ID    : {employee['employee_code']}")
        print(f"Employee       : {employee['full_name']}")
        print(f"Date           : {today}")
        print(f"Check-In       : {attendance['check_in']}")
        print(f"Check-Out      : {current_time}")
        print(
            f"Working Hours  : "
            f"{hours}h {minutes}m {seconds}s"
        )

        print("=" * 55)

        cursor.close()
        connection.close()

    except Exception as e:

        connection.rollback()

        print(f"❌ Check-out error: {e}")

        if connection.is_connected():
            connection.close()            




# ============================================================
# ADMIN - VIEW TODAY'S ATTENDANCE
# ============================================================

def view_today_attendance():

    connection = create_connection()

    if connection is None:
        return

    try:

        cursor = connection.cursor(dictionary=True)

        today = datetime.now().date()

        # --------------------------------------------------
        # GET TODAY'S ATTENDANCE
        # --------------------------------------------------

        query = """
            SELECT
                e.employee_code,
                e.full_name,
                d.department_name,
                a.check_in,
                a.check_out,
                a.working_hours,
                a.status
            FROM employees e
            INNER JOIN departments d
                ON e.department_id = d.department_id
            LEFT JOIN attendance a
                ON e.employee_id = a.employee_id
                AND a.attendance_date = %s
            WHERE e.status != 'Inactive'
            ORDER BY e.employee_id
        """

        cursor.execute(query, (today,))

        records = cursor.fetchall()

        if not records:

            print("\n❌ No employee records found!")

            cursor.close()
            connection.close()
            return

        # --------------------------------------------------
        # DISPLAY HEADER
        # --------------------------------------------------

        print("\n")
        print("=" * 120)
        print(" " * 45 + "TODAY'S ATTENDANCE")
        print("=" * 120)

        print(f"Date: {today}")

        print("-" * 120)

        print(
            f"{'ID':<10}"
            f"{'NAME':<22}"
            f"{'DEPARTMENT':<18}"
            f"{'CHECK-IN':<12}"
            f"{'CHECK-OUT':<12}"
            f"{'HOURS':<10}"
            f"{'STATUS':<12}"
        )

        print("-" * 120)

        # --------------------------------------------------
        # COUNTERS
        # --------------------------------------------------

        total_employees = len(records)

        present_count = 0
        late_count = 0
        absent_count = 0
        checked_out_count = 0
        currently_working_count = 0

        # --------------------------------------------------
        # DISPLAY RECORDS
        # --------------------------------------------------

        for record in records:

            check_in = record["check_in"]
            check_out = record["check_out"]
            working_hours = record["working_hours"]
            status = record["status"]

            # No attendance record
            if check_in is None:

                display_check_in = "--"
                display_check_out = "--"
                display_hours = "--"
                display_status = "Absent"

                absent_count += 1

            else:

                display_check_in = str(check_in)

                if check_out is None:
                    display_check_out = "--"
                    currently_working_count += 1

                else:
                    display_check_out = str(check_out)
                    checked_out_count += 1

                if working_hours is not None:
                    display_hours = f"{float(working_hours):.2f}"
                else:
                    display_hours = "--"

                display_status = status

                if status == "Present":
                    present_count += 1

                elif status == "Late":
                    late_count += 1

            print(
                f"{record['employee_code']:<10}"
                f"{record['full_name']:<22}"
                f"{record['department_name']:<18}"
                f"{display_check_in:<12}"
                f"{display_check_out:<12}"
                f"{display_hours:<10}"
                f"{display_status:<12}"
            )

        # --------------------------------------------------
        # SUMMARY
        # --------------------------------------------------

        print("-" * 120)

        print("\nATTENDANCE SUMMARY")
        print("-" * 40)

        print(f"Total Employees     : {total_employees}")
        print(f"Present             : {present_count}")
        print(f"Late                : {late_count}")
        print(f"Absent              : {absent_count}")
        print(f"Checked Out         : {checked_out_count}")
        print(f"Currently Working   : {currently_working_count}")

        print("-" * 40)

        cursor.close()
        connection.close()

    except Exception as e:

        print(f"❌ Error loading today's attendance: {e}")

        if connection.is_connected():
            connection.close()


# ============================================================
# ADMIN - VIEW EMPLOYEE ATTENDANCE HISTORY
# ============================================================

def view_employee_attendance():

    connection = create_connection()

    if connection is None:
        return

    try:

        cursor = connection.cursor(dictionary=True)

        # --------------------------------------------------
        # 1. GET EMPLOYEE ID
        # --------------------------------------------------

        print("\n")
        print("=" * 70)
        print("              EMPLOYEE ATTENDANCE HISTORY")
        print("=" * 70)

        employee_code = input("Enter Employee ID: ").strip().upper()

        if employee_code == "":
            print("\n❌ Employee ID cannot be empty!")

            cursor.close()
            connection.close()
            return

        # --------------------------------------------------
        # 2. CHECK EMPLOYEE
        # --------------------------------------------------

        cursor.execute("""
            SELECT
                e.employee_id,
                e.employee_code,
                e.full_name,
                e.email,
                e.phone,
                d.department_name,
                e.designation,
                e.status
            FROM employees e
            INNER JOIN departments d
                ON e.department_id = d.department_id
            WHERE e.employee_code = %s
        """, (employee_code,))

        employee = cursor.fetchone()

        if employee is None:

            print("\n❌ Employee not found!")

            cursor.close()
            connection.close()
            return

        # --------------------------------------------------
        # 3. DISPLAY EMPLOYEE INFORMATION
        # --------------------------------------------------

        print("\n")
        print("=" * 70)
        print("                 EMPLOYEE INFORMATION")
        print("=" * 70)

        print(f"Employee ID : {employee['employee_code']}")
        print(f"Name        : {employee['full_name']}")
        print(f"Department  : {employee['department_name']}")
        print(f"Designation : {employee['designation']}")
        print(f"Status      : {employee['status']}")

        print("=" * 70)

        # --------------------------------------------------
        # 4. GET ATTENDANCE HISTORY
        # --------------------------------------------------

        cursor.execute("""
            SELECT
                attendance_id,
                attendance_date,
                check_in,
                check_out,
                working_hours,
                status,
                remarks
            FROM attendance
            WHERE employee_id = %s
            ORDER BY attendance_date DESC
        """, (employee["employee_id"],))

        attendance_records = cursor.fetchall()

        # --------------------------------------------------
        # 5. NO ATTENDANCE RECORD
        # --------------------------------------------------

        if not attendance_records:

            print("\n❌ No attendance records found for this employee.")

            print("\n" + "=" * 70)

            cursor.close()
            connection.close()
            return

        # --------------------------------------------------
        # 6. DISPLAY ATTENDANCE TABLE
        # --------------------------------------------------

        print("\n")
        print("=" * 105)
        print(" " * 38 + "ATTENDANCE HISTORY")
        print("=" * 105)

        print(
            f"{'DATE':<15}"
            f"{'CHECK-IN':<14}"
            f"{'CHECK-OUT':<14}"
            f"{'HOURS':<12}"
            f"{'STATUS':<15}"
            f"{'REMARKS':<25}"
        )

        print("-" * 105)

        # --------------------------------------------------
        # 7. COUNTERS
        # --------------------------------------------------

        total_records = len(attendance_records)

        present_count = 0
        late_count = 0
        absent_count = 0
        checked_out_count = 0
        currently_working_count = 0

        total_working_hours = 0.0

        # --------------------------------------------------
        # 8. DISPLAY EACH RECORD
        # --------------------------------------------------

        for record in attendance_records:

            attendance_date = record["attendance_date"]
            check_in = record["check_in"]
            check_out = record["check_out"]
            working_hours = record["working_hours"]
            status = record["status"]
            remarks = record["remarks"]

            # ----------------------------------------------
            # CHECK-IN
            # ----------------------------------------------

            if check_in is not None:
                display_check_in = str(check_in)
            else:
                display_check_in = "--"

            # ----------------------------------------------
            # CHECK-OUT
            # ----------------------------------------------

            if check_out is not None:
                display_check_out = str(check_out)
                checked_out_count += 1
            else:
                display_check_out = "--"

                if check_in is not None:
                    currently_working_count += 1

            # ----------------------------------------------
            # WORKING HOURS
            # ----------------------------------------------

            if working_hours is not None:

                display_hours = f"{float(working_hours):.2f}"

                total_working_hours += float(working_hours)

            else:

                display_hours = "--"

            # ----------------------------------------------
            # STATUS
            # ----------------------------------------------

            if check_in is None:

                display_status = "Absent"
                absent_count += 1

            else:

                display_status = status

                if status == "Present":
                    present_count += 1

                elif status == "Late":
                    late_count += 1

                elif status == "Absent":
                    absent_count += 1

            # ----------------------------------------------
            # REMARKS
            # ----------------------------------------------

            if remarks is None or str(remarks).strip() == "":
                display_remarks = "--"
            else:
                display_remarks = str(remarks)

            # Limit long remarks so table remains readable
            if len(display_remarks) > 23:
                display_remarks = display_remarks[:20] + "..."

            # ----------------------------------------------
            # PRINT RECORD
            # ----------------------------------------------

            print(
                f"{str(attendance_date):<15}"
                f"{display_check_in:<14}"
                f"{display_check_out:<14}"
                f"{display_hours:<12}"
                f"{display_status:<15}"
                f"{display_remarks:<25}"
            )

        # --------------------------------------------------
        # 9. ATTENDANCE SUMMARY
        # --------------------------------------------------

        # Attendance percentage
        # Present + Late are considered attended days.

        attended_days = present_count + late_count

        if total_records > 0:
            attendance_percentage = (
                attended_days / total_records
            ) * 100
        else:
            attendance_percentage = 0

        average_working_hours = (
            total_working_hours / checked_out_count
            if checked_out_count > 0
            else 0
        )

        print("-" * 105)

        print("\n")
        print("=" * 60)
        print("                 ATTENDANCE SUMMARY")
        print("=" * 60)

        print(f"Total Attendance Records : {total_records}")
        print(f"Present                  : {present_count}")
        print(f"Late                     : {late_count}")
        print(f"Absent                   : {absent_count}")
        print(f"Checked Out              : {checked_out_count}")
        print(f"Currently Working        : {currently_working_count}")

        print(
            f"Total Working Hours      : "
            f"{total_working_hours:.2f}"
        )

        print(
            f"Average Working Hours    : "
            f"{average_working_hours:.2f}"
        )

        print(
            f"Attendance Percentage    : "
            f"{attendance_percentage:.2f}%"
        )

        print("=" * 60)

        cursor.close()
        connection.close()

    except Exception as e:

        print(
            f"\n❌ Error loading employee attendance: {e}"
        )

        if connection.is_connected():
            connection.close()



