from database import create_connection


# ============================================================
# CREATE NOTIFICATION
# ============================================================

def create_notification(user_id, title, message, notification_type="General"):
    connection = create_connection()

    if connection is None:
        return False

    try:
        cursor = connection.cursor()

        query = """
            INSERT INTO notifications
            (user_id, title, message, notification_type)
            VALUES (%s, %s, %s, %s)
        """

        cursor.execute(
            query,
            (user_id, title, message, notification_type)
        )

        connection.commit()

        cursor.close()
        connection.close()

        return True

    except Exception as e:
        print(f"❌ Notification error: {e}")

        if connection.is_connected():
            connection.close()

        return False


# ============================================================
# GET USER ID USING EMPLOYEE CODE
# ============================================================

def get_user_id_by_employee_code(employee_code):
    connection = create_connection()

    if connection is None:
        return None

    try:
        cursor = connection.cursor(dictionary=True)

        query = """
            SELECT user_id
            FROM users
            WHERE username = %s
              AND status = 'Active'
        """

        cursor.execute(query, (employee_code,))
        user = cursor.fetchone()

        cursor.close()
        connection.close()

        if user:
            return user["user_id"]

        return None

    except Exception as e:
        print(f"❌ Error finding user: {e}")

        if connection.is_connected():
            connection.close()

        return None


# ============================================================
# VIEW NOTIFICATIONS
# ============================================================

def view_notifications(user_id):
    connection = create_connection()

    if connection is None:
        return

    try:
        cursor = connection.cursor(dictionary=True)

        query = """
            SELECT
                notification_id,
                title,
                message,
                notification_type,
                is_read,
                created_at
            FROM notifications
            WHERE user_id = %s
            ORDER BY created_at DESC
        """

        cursor.execute(query, (user_id,))
        notifications = cursor.fetchall()

        print("\n" + "=" * 70)
        print("                     NOTIFICATIONS")
        print("=" * 70)

        if not notifications:
            print("\n📭 No notifications found.")
        else:
            for notification in notifications:

                if notification["is_read"] == 0:
                    status = "🔵 UNREAD"
                else:
                    status = "✓ Read"

                print(f"\n{status}")
                print(f"📌 {notification['title']}")
                print(f"📝 {notification['message']}")
                print(f"📂 Type       : {notification['notification_type']}")
                print(f"🕐 Created    : {notification['created_at']}")
                print("-" * 70)

        cursor.close()
        connection.close()

    except Exception as e:
        print(f"❌ Error loading notifications: {e}")

        if connection.is_connected():
            connection.close()


# ============================================================
# COUNT UNREAD NOTIFICATIONS
# ============================================================

def count_unread_notifications(user_id):
    connection = create_connection()

    if connection is None:
        return 0

    try:
        cursor = connection.cursor()

        query = """
            SELECT COUNT(*) 
            FROM notifications
            WHERE user_id = %s
              AND is_read = 0
        """

        cursor.execute(query, (user_id,))
        count = cursor.fetchone()[0]

        cursor.close()
        connection.close()

        return count

    except Exception as e:
        print(f"❌ Error counting notifications: {e}")

        if connection.is_connected():
            connection.close()

        return 0


# ============================================================
# MARK ONE NOTIFICATION AS READ
# ============================================================

def mark_notification_as_read(user_id):
    connection = create_connection()

    if connection is None:
        return

    try:
        cursor = connection.cursor(dictionary=True)

        query = """
            SELECT notification_id, title
            FROM notifications
            WHERE user_id = %s
              AND is_read = 0
            ORDER BY created_at DESC
        """

        cursor.execute(query, (user_id,))
        notifications = cursor.fetchall()

        if not notifications:
            print("\n📭 No unread notifications.")
            cursor.close()
            connection.close()
            return

        print("\n" + "=" * 60)
        print("             UNREAD NOTIFICATIONS")
        print("=" * 60)

        for i, notification in enumerate(notifications, start=1):
            print(
                f"{i}. {notification['title']}"
            )

        print("0. Cancel")

        try:
            choice = int(input("\nEnter notification number: "))
        except ValueError:
            print("❌ Invalid choice!")
            cursor.close()
            connection.close()
            return

        if choice == 0:
            cursor.close()
            connection.close()
            return

        if choice < 1 or choice > len(notifications):
            print("❌ Invalid notification number!")
            cursor.close()
            connection.close()
            return

        notification_id = notifications[choice - 1]["notification_id"]

        update_query = """
            UPDATE notifications
            SET is_read = 1
            WHERE notification_id = %s
              AND user_id = %s
        """

        cursor.execute(
            update_query,
            (notification_id, user_id)
        )

        connection.commit()

        print("✅ Notification marked as read.")

        cursor.close()
        connection.close()

    except Exception as e:
        print(f"❌ Error marking notification: {e}")

        if connection.is_connected():
            connection.close()


# ============================================================
# MARK ALL NOTIFICATIONS AS READ
# ============================================================

def mark_all_notifications_as_read(user_id):
    connection = create_connection()

    if connection is None:
        return

    try:
        cursor = connection.cursor()

        query = """
            UPDATE notifications
            SET is_read = 1
            WHERE user_id = %s
              AND is_read = 0
        """

        cursor.execute(query, (user_id,))
        connection.commit()

        if cursor.rowcount > 0:
            print(
                f"\n✅ {cursor.rowcount} notification(s) marked as read."
            )
        else:
            print("\n📭 No unread notifications.")

        cursor.close()
        connection.close()

    except Exception as e:
        print(f"❌ Error updating notifications: {e}")

        if connection.is_connected():
            connection.close()


# ============================================================
# NOTIFICATION MENU
# ============================================================

def notification_menu(user_id):
    while True:

        print("\n" + "=" * 60)
        print("                 NOTIFICATION MENU")
        print("=" * 60)

        unread_count = count_unread_notifications(user_id)

        print(f"🔔 Unread Notifications: {unread_count}")
        print("-" * 60)

        print("1. View Notifications")
        print("2. Mark Notification as Read")
        print("3. Mark All as Read")
        print("4. Back")

        print("=" * 60)

        choice = input("Enter your choice: ").strip()

        if choice == "1":
            view_notifications(user_id)

        elif choice == "2":
            mark_notification_as_read(user_id)

        elif choice == "3":
            mark_all_notifications_as_read(user_id)

        elif choice == "4":
            break

        else:
            print("❌ Invalid choice!")


# ============================================================
# TEST NOTIFICATION MODULE
# ============================================================

if __name__ == "__main__":

    print("=" * 60)
    print("           NOTIFICATION MODULE TEST")
    print("=" * 60)

    employee_code = input("Enter employee code: ").strip()

    user_id = get_user_id_by_employee_code(employee_code)

    if user_id is None:
        print("❌ Active user not found!")
    else:
        print(f"✅ User ID found: {user_id}")

        notification_menu(user_id)