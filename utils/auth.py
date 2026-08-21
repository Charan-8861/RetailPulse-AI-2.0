import sqlite3
import hashlib
import os


DB_PATH = "database/users.db"


# ============================================================
# DATABASE CONNECTION
# ============================================================

def get_connection():
    os.makedirs("database", exist_ok=True)

    return sqlite3.connect(
        DB_PATH,
        check_same_thread=False
    )


# ============================================================
# CREATE / UPDATE USERS TABLE
# ============================================================

def create_users_table():
    """
    Create the users table if it does not exist.

    Also upgrades an older RetailPulse database by adding
    the email column when necessary.
    """

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT,
            password TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )

    # --------------------------------------------------------
    # MIGRATE OLD DATABASE
    # --------------------------------------------------------

    cursor.execute(
        "PRAGMA table_info(users)"
    )

    columns = [
        row[1]
        for row in cursor.fetchall()
    ]

    if "email" not in columns:
        cursor.execute(
            """
            ALTER TABLE users
            ADD COLUMN email TEXT
            """
        )

    conn.commit()
    conn.close()


# ============================================================
# PASSWORD HASHING
# ============================================================

def hash_password(password):
    return hashlib.sha256(
        password.encode("utf-8")
    ).hexdigest()


# ============================================================
# REGISTER USER
# ============================================================

def register_user(
    username,
    email,
    password
):
    """
    Register a new RetailPulse user.
    """

    username = username.strip()
    email = email.strip().lower()

    # --------------------------------------------------------
    # BASIC VALIDATION
    # --------------------------------------------------------

    if not username:
        return False, "Username is required."

    if not email:
        return False, "Email address is required."

    if not password:
        return False, "Password is required."

    if len(username) < 3:
        return (
            False,
            "Username must contain at least 3 characters."
        )

    if len(password) < 6:
        return (
            False,
            "Password must contain at least 6 characters."
        )

    if (
        "@" not in email
        or "." not in email.split("@")[-1]
    ):
        return (
            False,
            "Please enter a valid email address."
        )

    conn = get_connection()
    cursor = conn.cursor()

    # --------------------------------------------------------
    # CHECK USERNAME
    # --------------------------------------------------------

    cursor.execute(
        """
        SELECT id
        FROM users
        WHERE LOWER(username) = LOWER(?)
        """,
        (username,)
    )

    if cursor.fetchone():

        conn.close()

        return (
            False,
            "Username already exists."
        )

    # --------------------------------------------------------
    # CHECK EMAIL
    # --------------------------------------------------------

    cursor.execute(
        """
        SELECT id
        FROM users
        WHERE LOWER(email) = LOWER(?)
        """,
        (email,)
    )

    if cursor.fetchone():

        conn.close()

        return (
            False,
            "An account already exists with this email."
        )

    # --------------------------------------------------------
    # HASH PASSWORD
    # --------------------------------------------------------

    hashed_password = hash_password(
        password
    )

    # --------------------------------------------------------
    # CREATE USER
    # --------------------------------------------------------

    try:

        cursor.execute(
            """
            INSERT INTO users (
                username,
                email,
                password
            )
            VALUES (?, ?, ?)
            """,
            (
                username,
                email,
                hashed_password
            )
        )

        conn.commit()
        conn.close()

        return (
            True,
            "Account created successfully."
        )

    except sqlite3.IntegrityError:

        conn.close()

        return (
            False,
            "Unable to create account. Username may already exist."
        )

    except Exception as error:

        conn.close()

        return (
            False,
            f"Unable to create account: {error}"
        )


# ============================================================
# AUTHENTICATE USER
# ============================================================

def authenticate_user(
    username,
    password
):
    """
    Authenticate user using username and password.
    """

    username = username.strip()

    if not username or not password:
        return False, None

    hashed_password = hash_password(
        password
    )

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT
            id,
            username,
            email
        FROM users
        WHERE LOWER(username) = LOWER(?)
        AND password = ?
        """,
        (
            username,
            hashed_password
        )
    )

    user = cursor.fetchone()

    conn.close()

    if user:
        return True, user

    return False, None


# ============================================================
# VERIFY USER FOR PASSWORD RESET
# ============================================================

def verify_reset_user(
    username,
    email
):
    """
    Verify that username and email belong
    to the same registered account.
    """

    username = username.strip()
    email = email.strip().lower()

    if not username or not email:
        return False

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT id
        FROM users
        WHERE LOWER(username) = LOWER(?)
        AND LOWER(email) = LOWER(?)
        """,
        (
            username,
            email
        )
    )

    user = cursor.fetchone()

    conn.close()

    return user is not None


# ============================================================
# RESET PASSWORD
# ============================================================

def reset_password(
    username,
    email,
    new_password
):
    """
    Reset password after verifying
    username and registered email.
    """

    username = username.strip()
    email = email.strip().lower()

    # --------------------------------------------------------
    # VALIDATION
    # --------------------------------------------------------

    if not username:
        return False, "Username is required."

    if not email:
        return False, "Email address is required."

    if not new_password:
        return False, "New password is required."

    if len(new_password) < 6:
        return (
            False,
            "Password must contain at least 6 characters."
        )

    # --------------------------------------------------------
    # VERIFY ACCOUNT
    # --------------------------------------------------------

    if not verify_reset_user(
        username,
        email
    ):

        return (
            False,
            "Username and registered email do not match."
        )

    # --------------------------------------------------------
    # HASH NEW PASSWORD
    # --------------------------------------------------------

    hashed_password = hash_password(
        new_password
    )

    # --------------------------------------------------------
    # UPDATE PASSWORD
    # --------------------------------------------------------

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        UPDATE users
        SET password = ?
        WHERE LOWER(username) = LOWER(?)
        AND LOWER(email) = LOWER(?)
        """,
        (
            hashed_password,
            username,
            email
        )
    )

    conn.commit()

    updated_rows = cursor.rowcount

    conn.close()

    if updated_rows > 0:

        return (
            True,
            "Password reset successfully."
        )

    return (
        False,
        "Unable to reset password."
    )


# ============================================================
# CHECK EMAIL EXISTS
# ============================================================

def email_exists(email):
    """
    Check whether an email is already registered.
    """

    email = email.strip().lower()

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT id
        FROM users
        WHERE LOWER(email) = LOWER(?)
        """,
        (email,)
    )

    result = cursor.fetchone()

    conn.close()

    return result is not None