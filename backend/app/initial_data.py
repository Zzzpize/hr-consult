from .core.redis_client import redis_client

def create_initial_admin():
    """
    Проверяет наличие пользователя 'admin' и создает его, если он отсутствует.
    """
    print("Checking for initial admin user...")
    admin_user = redis_client.get_user_by_username("admin")
    
    if admin_user:
        print("Admin user already exists.")
    else:
        print("Admin user not found, creating one...")
        redis_client.create_user(
            name="Администратор",
            role="Admin",
            username="admin",
            password="admin"
        )
        print("Initial admin user 'admin' with password 'admin' created successfully.")