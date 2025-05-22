from functools import wraps
from flask import request, jsonify 
from uuid import UUID
from typing import Optional, Callable, Any

class AuthenticatedUser:
    def __init__(self, id: Optional[UUID] = None, email: Optional[str] = None, role: Optional[str] = None, claims: Optional[dict] = None):
        self.id = id
        self.email = email
        self.role = role
        self.claims = claims if claims is not None else {}

def token_required(f: Callable[..., Any]) -> Callable[..., Any]:
    @wraps(f)
    def decorated_function(*args, **kwargs):
        simulated_user = AuthenticatedUser(id=UUID('00000000-0000-0000-0000-000000000000'), email="test@example.com", role="authenticated")
        return f(simulated_user, *args, **kwargs)
    return decorated_function

def admin_required(f: Callable[..., Any]) -> Callable[..., Any]:
    @wraps(f)
    def decorated_function(*args, **kwargs):
        simulated_admin_user = AuthenticatedUser(id=UUID('11111111-1111-1111-1111-111111111111'), email="admin@example.com", role="admin")
        return f(simulated_admin_user, *args, **kwargs)
    return decorated_function