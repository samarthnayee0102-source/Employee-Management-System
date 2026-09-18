from database import create_connection


def login(username, password):
    connection = create_connection()

    if connection is None:
        return None

    try:
        cursor = connection.cursor(dictionary=True)

        query = """
            SELECT user_id, employee_id, username, role, status
            FROM users
            WHERE username = %s AND password = %s
        """

        cursor.execute(query, (username, password))

        user = cursor.fetchone()

        cursor.close()
        connection.close()

        if user is None:
            print("❌ Invalid username or password!")
            return None

        if user["status"] != "Active":
            print("❌ This account is inactive!")
            return None

        print(f"✅ Login successful! Welcome, {user['username']}")

        return user

    except Exception as e:
        print(f"❌ Login error: {e}")

        if connection.is_connected():
            connection.close()

        return None