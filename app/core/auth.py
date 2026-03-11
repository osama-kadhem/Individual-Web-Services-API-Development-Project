from datetime import datetime, timedelta
from typing import Optional, List
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status, Security
from fastapi.security import OAuth2PasswordBearer, APIKeyHeader, APIKeyQuery
from app.core.config import settings
from app.schemas.token import TokenData

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/auth/login",
    auto_error=False
)

# Legacy API Key header/query for backward compatibility
api_key_header = APIKeyHeader(name="X-API-KEY", auto_error=False)
api_key_query = APIKeyQuery(name="X-API-KEY", auto_error=False)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against its hash."""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Generate a bcrypt hash of a password."""
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Generate a JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

async def get_current_user(
    token: Optional[str] = Depends(oauth2_scheme),
    api_key_h: Optional[str] = Security(api_key_header),
    api_key_q: Optional[str] = Security(api_key_query)
) -> TokenData:
    """
    Validates either a JWT token or a master API key.
    Returns TokenData containing the user's email and role.
    """
    # 1. Check master API key (Legacy/Admin bypass)
    if api_key_h == settings.API_KEY or api_key_q == settings.API_KEY:
        return TokenData(email="admin@ironmind.com", role="coach")

    # 2. Check JWT Token
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing Authentication Token or API Key",
            headers={"WWW-Authenticate": "Bearer"},
        )

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        email: str = payload.get("sub")
        role: str = payload.get("role", "athlete")
        if email is None:
            raise credentials_exception
        token_data = TokenData(email=email, role=role)
        return token_data
    except JWTError:
        raise credentials_exception

class RoleChecker:
    """Dependency for checking required roles."""
    def __init__(self, allowed_roles: List[str]):
        self.allowed_roles = allowed_roles

    def __call__(self, current_user: TokenData = Depends(get_current_user)):
        if current_user.role not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Operation not permitted. Required roles: {self.allowed_roles}"
            )
        return current_user
