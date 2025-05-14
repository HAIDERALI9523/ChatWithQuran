import auth as auth
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    # Initialize the users file
    auth.initialize_users_file()

    # Test registration
    username = "testuser"
    password = "testpass"
    email = "test@example.com"

    success, message = auth.register_user(username, password, email)
    print(f"Registration: {success}, {message}")

    # Test authentication
    success, message = auth.authenticate_user(username, password)
    print(f"Authentication: {success}, {message}")

    # Test wrong password
    success, message = auth.authenticate_user(username, "wrongpass")
    print(f"Wrong password: {success}, {message}")

    # Test non-existent user
    success, message = auth.authenticate_user("nonexistent", "anypass")
    print(f"Non-existent user: {success}, {message}")

    # Test get email
    email = auth.get_user_email(username)
    print(f"Email for {username}: {email}")


if __name__ == "__main__":
    main()