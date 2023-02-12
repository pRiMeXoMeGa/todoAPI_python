from datetime import datetime
from pydantic import BaseModel, EmailStr
from typing import Optional, List

# all these classes are pydantic schemas that is used for validation and 
# check the input variable given by user for proper datatypes  and 
# also check the response of the endpoint to be in appropriate format 
class UserBase(BaseModel):
    email: EmailStr
    password:str
    




class UserCreate(UserBase):
    fullname:str
    pass

class UserOut(BaseModel):
    id:int
    email:EmailStr
    fullname:str
    created_at:datetime
    class Config():
        orm_mode = True

class UserLogin(UserBase):
    pass





class Token(BaseModel):
    access_token:str
    token_type:str
    user:UserOut
    class Config():
        orm_mode = True

class JWTPayload(BaseModel):
    id:Optional[str] = None





class Todos(BaseModel):
    todo: str
    category:int
    completed: Optional[bool] = False

class TodosCreate(Todos):
    pass

class TodosOut(Todos):
    id:int
    created_at:datetime
    class Config:
        orm_mode = True

class TodosOutAll(BaseModel):
    todos:List[TodosOut]
    user:UserOut
    class Config:
        orm_mode = True





class CategoryCreate(BaseModel):
    category:Optional[str]
    sharedWith:Optional[List[EmailStr]]
    isShared:Optional[bool]

class CategoryUpdate(BaseModel):
    category:Optional[str]
    isShared:Optional[bool]

class CategoryOut(BaseModel):
    id:int
    category:str
    user_id:int
    isShared:bool
    created_at:datetime
    class Config:
        orm_mode = True

class SharedUser(BaseModel):
    user_id:int
    Category:CategoryOut
    class Config:
        orm_mode = True

class SharedUserID(BaseModel):
    user_id:int
    class Config:
        orm_mode = True

class SharedOut(CategoryOut):
    sharedWith:Optional[List[UserOut]]
    class Config:
        orm_mode = True

class AllCategoryOut(BaseModel):
    categories:List[SharedOut]
    user:UserOut
    class Config:
        orm_mode = True

class SharedData(BaseModel):
    user_id:EmailStr
    category_id:int
    class Config:
        orm_mode = True

class SharedDataOut(BaseModel):
    user_id:int
    category_id:int
    class Config:
        orm_mode = True