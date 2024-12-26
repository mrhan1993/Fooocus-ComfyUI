from uuid import uuid4

# from pydantic import BaseModel, Field
from uuid import uuid4
from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship


class UserRoleLink(SQLModel, table=True):
    user_uid: str = Field(foreign_key="user.uid", primary_key=True)
    role_id: int = Field(foreign_key="role.id", primary_key=True)

class RolePermissionLink(SQLModel, table=True):
    role_id: int = Field(foreign_key="role.id", primary_key=True)
    permission_id: int = Field(foreign_key="permission.id", primary_key=True)

class Permission(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    name: str = Field(description="Permission name", unique=True)
    roles: List["Role"] = Relationship(back_populates="permissions", link_model=RolePermissionLink)

class Role(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    name: str = Field(description="Role name", unique=True)
    users: List["User"] = Relationship(back_populates="roles", link_model=UserRoleLink)
    permissions: List[Permission] = Relationship(back_populates="roles", link_model=RolePermissionLink)

class User(SQLModel, table=True):
    uid: str = Field(default_factory=lambda: uuid4().hex, description="User id", primary_key=True)
    username: str = Field(description="User name", unique=True)
    nick_name: str = Field(default="", description="User nick name")
    email: Optional[str] = Field(default=None, description="User email")
    full_name: Optional[str] = Field(default=None, description="User full name")
    enabled: bool = Field(default=True, description="User enabled")
    roles: List[Role] = Relationship(back_populates="users", link_model=UserRoleLink)

class UserInDB(User):
    hashed_password: str = Field(description="User password")

class UserCreate(SQLModel, table=True):
    username: str = Field(description="User name")
    password: str = Field(description="User password")
    nick_name: str = Field(default="", description="User nick name")
    email: Optional[str] = Field(default="", description="User email")
    full_name: Optional[str] = Field(default="", description="User full name")

class TokenData(SQLModel, table=True):
    username: Optional[str] = Field(description="User name")