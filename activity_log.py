from database import create_connection


# ============================================================
# CREATE ACTIVITY LOG
# ============================================================

def create_activity_log(user_id, action, description):
    connection = create_connection()

    if connection is None:
        return False

    try:
        cursor = connection.cursor()

        query = """
            INSERT INTO activity_logs
            (user_id, action, description)
            VALUES (%s, %s, %s)
        """

        cursor.execute(
            query,
            (user_id, action, description)
        )

        connection.commit()

        cursor.close()
        connection.close()

        return True

    except Exception as e:
        print(f"❌ Activity log error: {e}")

        if connection.is_connected():
            connection.close()

        return False


# ============================================================
# VIEW ALL ACTIVITY LOGS - ADMIN
# ============================================================

def view_all_activity_logs():
    connection = create_connection()

    if connection is None:
        return

    try:
        cursor = connection.cursor(dictionary=True)

        query = """
            SELECT
                a.log_id,
                a.user_id,
                u.username,
                u.role,
                a.action,
                a.description,
                a.created_at
            FROM activity_logs a
            LEFT JOIN users u
                ON a.user_id = u.user_id
            ORDER BY a.created_at DESC
        """

        cursor.execute(query)
        logs = cursor.fetchall()

        print("\n" + "=" * 80)
        print("                     ACTIVITY LOGS")
        print("=" * 80)

        if not logs:
            print("\n📭 No activity logs found.")
        else:
            for log in logs:
                print(f"\n🆔 Log ID     : {log['log_id']}")
                print(f"👤 User       : {log['username'] or 'Unknown'}")
                print(f"🔐 Role       : {log['role'] or 'Unknown'}")
                print(f"⚙️ Action     : {log['action']}")
                print(f"📝 Description: {log['description']}")
                print(f"🕐 Time       : {log['created_at']}")
                print("-" * 80)

        cursor.close()
        connection.close()

    except Exception as e:
        print(f"❌ Error loading activity logs: {e}")

        if connection.is_connected():
            connection.close()


# ============================================================
# VIEW USER'S ACTIVITY LOGS
# ============================================================

def view_my_activity_logs(user_id):
    connection = create_connection()

    if connection is None:
        return

    try:
        cursor = connection.cursor(dictionary=True)

        query = """
            SELECT
                log_id,
                action,
                description,
                created_at
            FROM activity_logs
            WHERE user_id = %s
            ORDER BY created_at DESC
        """

        cursor.execute(query, (user_id,))
        logs = cursor.fetchall()

        print("\n" + "=" * 70)
        print("                   MY ACTIVITY")
        print("=" * 70)

        if not logs:
            print("\n📭 No activity found.")
        else:
            for log in logs:
                print(f"\n⚙️ Action     : {log['action']}")
                print(f"📝 Description: {log['description']}")
                print(f"🕐 Time       : {log['created_at']}")
                print("-" * 70)

        cursor.close()
        connection.close()

    except Exception as e:
        print(f"❌ Error loading your activity: {e}")

        if connection.is_connected():
            connection.close()


# ============================================================
# DELETE OLD LOGS
# ============================================================

def delete_old_logs():
    connection = create_connection()

    if connection is None:
        return

    try:
        cursor = connection.cursor()

        print("\n" + "=" * 60)
        print("              DELETE OLD ACTIVITY LOGS")
        print("=" * 60)

        try:
            days = int(
                input("Delete logs older than how many days? ").strip()
            )
        except ValueError:
            print("❌ Please enter a valid number.")
            cursor.close()
            connection.close()
            return

        if days <= 0:
            print("❌ Days must be greater than 0.")
            cursor.close()
            connection.close()
            return

        query = """
            DELETE FROM activity_logs
            WHERE created_at < DATE_SUB(NOW(), INTERVAL %s DAY)
        """

        cursor.execute(query, (days,))
        connection.commit()

        print(
            f"✅ {cursor.rowcount} old activity log(s) deleted."
        )

        cursor.close()
        connection.close()

    except Exception as e:
        print(f"❌ Error deleting logs: {e}")

        if connection.is_connected():
            connection.close()


# ============================================================
# ACTIVITY LOG MENU
# ============================================================

def activity_log_menu():
    while True:

        print("\n" + "=" * 60)
        print("                 ACTIVITY LOG MENU")
        print("=" * 60)

        print("1. View All Activity Logs")
        print("2. Delete Old Logs")
        print("3. Back")

        print("=" * 60)

        choice = input("Enter your choice: ").strip()

        if choice == "1":
            view_all_activity_logs()

        elif choice == "2":
            delete_old_logs()

        elif choice == "3":
            break

        else:
            print("❌ Invalid choice!")


# ============================================================
# TEST ACTIVITY LOG MODULE
# ============================================================

if __name__ == "__main__":

    print("=" * 60)
    print("             ACTIVITY LOG MODULE TEST")
    print("=" * 60)

    print("\n1. Create Test Log")
    print("2. View All Logs")

    choice = input("\nEnter your choice: ").strip()

    if choice == "1":

        try:
            user_id = int(input("Enter User ID: ").strip())
        except ValueError:
            print("❌ Invalid User ID!")
            exit()

        action = input("Enter action: ").strip()
        description = input("Enter description: ").strip()

        if not action:
            print("❌ Action cannot be empty!")

        elif not description:
            print("❌ Description cannot be empty!")

        elif create_activity_log(user_id, action, description):
            print("✅ Activity log created successfully!")

        else:
            print("❌ Failed to create activity log.")

    elif choice == "2":
        view_all_activity_logs()

    else:
        print("❌ Invalid choice!")