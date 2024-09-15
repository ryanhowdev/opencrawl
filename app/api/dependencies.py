from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

# OAuth2 Password Bearer setup
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Example function to verify token (can be extended for real use cases)
def verify_token(token: str = Depends(oauth2_scheme)):
    if token != "mysecrettoken":  # Replace with a real token validation logic
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return token
