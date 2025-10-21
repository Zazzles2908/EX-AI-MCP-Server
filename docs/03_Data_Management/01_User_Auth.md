# User Authentication & Authorization

## Purpose & Responsibility

This component implements secure user authentication using JWT tokens and Role-Based Access Control (RBAC) to manage user access to resources and functionalities.

## Authentication Flow

### JWT Token Service

```python
# services/auth_service.py
import jwt
import bcrypt
from datetime import datetime, timedelta
from typing import Optional, Dict

class AuthService:
    def __init__(self, jwt_secret: str, token_expiry: int = 86400):
        self.jwt_secret = jwt_secret
        self.token_expiry = token_expiry  # seconds
    
    async def authenticate_user(
        self, 
        email: str, 
        password: str
    ) -> Dict:
        """Authenticate user and return JWT token"""
        # Find user
        user = await self.find_user_by_email(email)
        if not user:
            return {"success": False, "error": "Invalid credentials"}
        
        # Verify password
        if not bcrypt.checkpw(password.encode(), user.password_hash):
            return {"success": False, "error": "Invalid credentials"}
        
        # Generate token
        token = self.generate_token(user)
        
        # Update last login
        await self.update_last_login(user.id)
        
        return {
            "success": True,
            "token": token,
            "user": {
                "id": user.id,
                "email": user.email,
                "name": user.name,
                "roles": user.roles
            }
        }
    
    async def register_user(
        self, 
        email: str, 
        password: str, 
        name: str
    ) -> Dict:
        """Register new user"""
        # Check if user exists
        existing = await self.find_user_by_email(email)
        if existing:
            return {"success": False, "error": "User already exists"}
        
        # Hash password
        password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
        
        # Create user
        user = await self.create_user({
            "email": email,
            "password_hash": password_hash,
            "name": name,
            "roles": ["user"]  # Default role
        })
        
        # Generate token
        token = self.generate_token(user)
        
        return {
            "success": True,
            "token": token,
            "user": {
                "id": user.id,
                "email": user.email,
                "name": user.name,
                "roles": user.roles
            }
        }
    
    def generate_token(self, user) -> str:
        """Generate JWT token"""
        payload = {
            "user_id": user.id,
            "email": user.email,
            "roles": user.roles,
            "exp": datetime.utcnow() + timedelta(seconds=self.token_expiry)
        }
        return jwt.encode(payload, self.jwt_secret, algorithm="HS256")
    
    def verify_token(self, token: str) -> Optional[Dict]:
        """Verify JWT token"""
        try:
            payload = jwt.decode(token, self.jwt_secret, algorithms=["HS256"])
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
```

## Role-Based Access Control (RBAC)

### Permission System

```python
# services/rbac_service.py
from typing import List, Dict

class RBACService:
    def __init__(self):
        self.permissions = self.initialize_permissions()
    
    def initialize_permissions(self) -> Dict[str, List[str]]:
        """Define permissions for each role"""
        return {
            "admin": [
                "user.create",
                "user.read",
                "user.update",
                "user.delete",
                "model.create",
                "model.read",
                "model.update",
                "model.delete",
                "prompt.create",
                "prompt.read",
                "prompt.update",
                "prompt.delete",
                "system.configure"
            ],
            "moderator": [
                "user.read",
                "user.update",
                "model.read",
                "model.update",
                "prompt.create",
                "prompt.read",
                "prompt.update",
                "prompt.delete"
            ],
            "user": [
                "model.read",
                "prompt.read",
                "prompt.create",
                "file.create",
                "file.read",
                "file.update",
                "file.delete"
            ],
            "guest": [
                "model.read",
                "prompt.read"
            ]
        }
    
    def has_permission(self, user_roles: List[str], permission: str) -> bool:
        """Check if user has required permission"""
        for role in user_roles:
            if permission in self.permissions.get(role, []):
                return True
        return False
    
    def get_permissions(self, role: str) -> List[str]:
        """Get all permissions for a role"""
        return self.permissions.get(role, [])
```

## Middleware

### Authentication Middleware

```python
# middleware/auth_middleware.py
from fastapi import Request, HTTPException
from services.auth_service import AuthService

async def authenticate(request: Request):
    """Verify JWT token from request"""
    auth_header = request.headers.get("Authorization")
    
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    token = auth_header[7:]  # Remove "Bearer " prefix
    
    auth_service = AuthService(jwt_secret=settings.JWT_SECRET)
    payload = auth_service.verify_token(token)
    
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    # Attach user info to request
    request.state.user = {
        "id": payload["user_id"],
        "email": payload["email"],
        "roles": payload["roles"]
    }
```

### Authorization Middleware

```python
# middleware/auth_middleware.py
from functools import wraps
from fastapi import Request, HTTPException
from services.rbac_service import RBACService

def authorize(permission: str):
    """Decorator to check user permissions"""
    def decorator(func):
        @wraps(func)
        async def wrapper(request: Request, *args, **kwargs):
            if not hasattr(request.state, "user"):
                raise HTTPException(status_code=401, detail="Unauthorized")
            
            rbac = RBACService()
            if not rbac.has_permission(request.state.user["roles"], permission):
                raise HTTPException(status_code=403, detail="Forbidden")
            
            return await func(request, *args, **kwargs)
        return wrapper
    return decorator
```

## API Routes

### Authentication Endpoints

```python
# routes/auth.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from services.auth_service import AuthService

router = APIRouter()
auth_service = AuthService(jwt_secret=settings.JWT_SECRET)

class LoginRequest(BaseModel):
    email: str
    password: str

class RegisterRequest(BaseModel):
    email: str
    password: str
    name: str

@router.post("/login")
async def login(request: LoginRequest):
    result = await auth_service.authenticate_user(
        email=request.email,
        password=request.password
    )
    
    if not result["success"]:
        raise HTTPException(status_code=401, detail=result["error"])
    
    return {
        "token": result["token"],
        "user": result["user"]
    }

@router.post("/register")
async def register(request: RegisterRequest):
    if len(request.password) < 8:
        raise HTTPException(
            status_code=400, 
            detail="Password must be at least 8 characters"
        )
    
    result = await auth_service.register_user(
        email=request.email,
        password=request.password,
        name=request.name
    )
    
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["error"])
    
    return {
        "token": result["token"],
        "user": result["user"]
    }

@router.post("/logout")
async def logout():
    # Token invalidation handled client-side
    return {"message": "Logged out successfully"}
```

### Protected Routes Example

```python
# routes/users.py
from fastapi import APIRouter, Request, Depends
from middleware.auth_middleware import authenticate, authorize

router = APIRouter()

@router.get("/users")
@authorize("user.read")
async def list_users(request: Request):
    # Only users with "user.read" permission can access
    users = await get_all_users()
    return {"users": users}

@router.post("/users")
@authorize("user.create")
async def create_user(request: Request, user_data: dict):
    # Only users with "user.create" permission can access
    user = await create_new_user(user_data)
    return {"user": user}
```

## Configuration

### Environment Variables

```bash
# .env
JWT_SECRET=your-secret-key-change-in-production
JWT_EXPIRY=86400  # 24 hours in seconds
BCRYPT_ROUNDS=12
```

### User Schema

```python
# models/user.py
from datetime import datetime
from typing import List

class User:
    def __init__(
        self,
        id: str,
        email: str,
        password_hash: bytes,
        name: str,
        roles: List[str],
        is_active: bool = True,
        created_at: datetime = None,
        last_login: datetime = None
    ):
        self.id = id
        self.email = email
        self.password_hash = password_hash
        self.name = name
        self.roles = roles
        self.is_active = is_active
        self.created_at = created_at or datetime.utcnow()
        self.last_login = last_login
```

## Best Practices

1. **Password Security**: Use bcrypt with sufficient rounds (12+)
2. **Token Expiry**: Set reasonable expiry times (24 hours recommended)
3. **HTTPS Only**: Always use HTTPS in production
4. **Secret Management**: Store JWT secret in environment variables
5. **Permission Granularity**: Define fine-grained permissions

## Integration Points

- **API Layer**: Protects endpoints with authentication/authorization
- **Supabase**: Stores user data and audit logs
- **Frontend**: Manages tokens in HTTP-only cookies
- **WebSocket**: Validates tokens for WebSocket connections

