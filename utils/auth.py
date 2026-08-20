import os
import sqlite3
import hashlib
import hmac
import secrets


# ============================================================
# PROJECT / DATABASE PATH
# ============================================================

UTILS_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

BASE_DIR = os.path.dirname(
    UTILS_DIR
)

DATABASE_DIR = os.path.join(
    BASE_DIR,
    "database"
)

DB_PATH = os.path.join(
    DATABASE_DIR,
    "users.db"
)


# ============================================================
# DATABASE CONNECTION
# ============================================================

def get_connection():

    os.makedirs(
        DATABASE_DIR,
        exist_ok=True
    )

    connection = sqlite3.connect(
        DB_PATH,
        check_same_thread=False
    )

    return connection


# ============================================================
# CREATE USERS TABLE
# ============================================================

def create_users_table():

    connection = get_connection()

    try:

        cursor = connection.cursor()

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )

        connection.commit()

    finally:

        connection.close()


# ============================================================
# PASSWORD HASHING
# ============================================================

def hash_password(
    password,
    salt=None
):
    """
    Hash a password using PBKDF2-HMAC-SHA256.

    Stored format:
    salt$hash
    """

    if password is None:
        raise ValueError(
            "Password cannot be None."
        )

    password = str(
        password
    )


    if salt is None:

        salt = secrets.token_hex(
            16
        )


    derived_key = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode(
            "utf-8"
        ),
        salt.encode(
            "utf-8"
        ),
        200_000
    )


    password_hash = derived_key.hex()


    return (
        f"{salt}${password_hash}"
    )


# ============================================================
# PASSWORD VERIFICATION
# ============================================================

def verify_password(
    password,
    stored_password
):
    """
    Verify a password against its stored PBKDF2 hash.

    Also supports the older SHA-256 hashes from
    the earlier RetailPulse version.
    """

    if (
        password is None
        or
        stored_password is None
    ):
        return False


    password = str(
        password
    )


    stored_password = str(
        stored_password
    )


    # ========================================================
    # NEW PBKDF2 FORMAT
    # ========================================================

    if "$" in stored_password:

        try:

            salt, saved_hash = (
                stored_password.split(
                    "$",
                    1
                )
            )


            calculated = hashlib.pbkdf2_hmac(
                "sha256",
                password.encode(
                    "utf-8"
                ),
                salt.encode(
                    "utf-8"
                ),
                200_000
            ).hex()


            return hmac.compare_digest(
                calculated,
                saved_hash
            )

        except Exception:

            return False


    # ========================================================
    # LEGACY SHA-256 SUPPORT
    # ========================================================

    legacy_hash = hashlib.sha256(
        password.encode(
            "utf-8"
        )
    ).hexdigest()


    return hmac.compare_digest(
        legacy_hash,
        stored_password
    )


# ============================================================
# USERNAME CLEANING
# ============================================================

def normalize_username(
    username
):
    """
    Normalize username input.
    """

    if username is None:
        return ""

    return str(
        username
    ).strip()


# ============================================================
# REGISTER USER
# ============================================================

def register_user(
    username,
    password
):

    username = normalize_username(
        username
    )


    # ========================================================
    # VALIDATION
    # ========================================================

    if not username:

        return (
            False,
            "Username is required."
        )


    if not password:

        return (
            False,
            "Password is required."
        )


    if len(
        username
    ) < 3:

        return (
            False,
            "Username must contain at least 3 characters."
        )


    if len(
        username
    ) > 50:

        return (
            False,
            "Username must contain 50 characters or fewer."
        )


    if len(
        password
    ) < 6:

        return (
            False,
            "Password must contain at least 6 characters."
        )


    # ========================================================
    # PASSWORD HASH
    # ========================================================

    hashed_password = hash_password(
        password
    )


    connection = None


    try:

        connection = get_connection()

        cursor = connection.cursor()


        cursor.execute(
            """
            INSERT INTO users (
                username,
                password
            )
            VALUES (?, ?)
            """,
            (
                username,
                hashed_password
            )
        )


        connection.commit()


        return (
            True,
            "Account created successfully."
        )


    except sqlite3.IntegrityError:

        return (
            False,
            "Username already exists."
        )


    except sqlite3.Error as error:

        return (
            False,
            f"Unable to create account: {error}"
        )


    finally:

        if connection is not None:
            connection.close()


# ============================================================
# AUTHENTICATE USER
# ============================================================

def authenticate_user(
    username,
    password
):

    username = normalize_username(
        username
    )


    if (
        not username
        or
        not password
    ):

        return (
            False,
            None
        )


    connection = None


    try:

        connection = get_connection()

        cursor = connection.cursor()


        # Fetch the stored password hash first.
        cursor.execute(
            """
            SELECT
                id,
                username,
                password
            FROM users
            WHERE username = ?
            """,
            (
                username,
            )
        )


        user_record = cursor.fetchone()


        if user_record is None:

            return (
                False,
                None
            )


        user_id = (
            user_record[0]
        )

        stored_username = (
            user_record[1]
        )

        stored_password = (
            user_record[2]
        )


        password_valid = verify_password(
            password,
            stored_password
        )


        if not password_valid:

            return (
                False,
                None
            )


        # ====================================================
        # OPTIONAL LEGACY HASH UPGRADE
        # ====================================================
        # Existing users created with the older SHA-256
        # implementation are automatically upgraded after
        # a successful login.
        # ====================================================

        if "$" not in stored_password:

            new_password_hash = (
                hash_password(
                    password
                )
            )


            cursor.execute(
                """
                UPDATE users
                SET password = ?
                WHERE id = ?
                """,
                (
                    new_password_hash,
                    user_id
                )
            )


            connection.commit()


        # app.py expects user[1] to contain username.
        user = (
            user_id,
            stored_username
        )


        return (
            True,
            user
        )


    except sqlite3.Error:

        return (
            False,
            None
        )


    finally:

        if connection is not None:
            connection.close()