from ..models.user import UserResponse as User

def is_premium_user(user: User) -> bool:
    """
    Kullanıcının premium üye olup olmadığını kontrol eder.
    """
    return user.subscription_type == "premium" 