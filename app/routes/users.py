from fastapi import APIRouter, Depends, status, HTTPException, Response
from typing import List
from sqlalchemy.orm import Session
from .. import database, oauth2, schemas, models, utils

router = APIRouter(
    prefix="/users",
    tags=['Users']
)

@router.get(
            "/", 
            status_code=status.HTTP_200_OK, 
            response_model=List[schemas.UserOut]
            )
def get_all_users(
            db:Session=Depends(database.get_db),
            logged_user:Session=Depends(oauth2.get_current_user)):
    user_list = db.query(models.User).all()
    return user_list



@router.get(
            "/{id}", 
            status_code=status.HTTP_200_OK, 
            response_model=schemas.UserOut
            )
def get_users(
            id:int, 
            db:Session=Depends(database.get_db),
            logged_user:Session=Depends(oauth2.get_current_user)
            ):
    user = db.query(models.User).filter(models.User.id==id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"User with id {id} not found...")
    return user



@router.post(
            "/", 
            status_code=status.HTTP_201_CREATED, 
            response_model=schemas.UserOut
            )
def create_users(
            user:schemas.UserCreate, 
            db:Session=Depends(database.get_db)
            ):
    user_found = db.query(models.User).filter(user.email == models.User.email).first()
    if user_found:
        raise HTTPException(
                            status_code=status.HTTP_302_FOUND, 
                            detail=f"User '{user.email}' already exist..."
                            )
    hashed_password = utils.hash(user.password)
    user.password = hashed_password
    new = models.User(**user.dict())
    db.add(new)
    db.commit()
    db.refresh(new)
    return new



@router.put(
           "/{id}", 
           status_code=status.HTTP_202_ACCEPTED, 
           response_model=schemas.UserOut
           )
def update_users(
            id:int, user:schemas.UserCreate, 
            db:Session=Depends(database.get_db),
            logged_user:Session=Depends(oauth2.get_current_user)
            ):
    user_query = db.query(models.User).filter(id==models.User.id)
    user_found = user_query.first()
    if not user_found:
        raise HTTPException(
                            status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"User with email '{user.email}' not found..."
                            )
    hashed_pwd = utils.hash(user.password)
    user.password = hashed_pwd
    user_query.update(user.dict(),synchronize_session=False)
    db.commit()
    return user_query.first()



@router.delete("/{id}")
def delete_users(
                id:int,
                db:Session=Depends(database.get_db),
                logged_user:Session=Depends(oauth2.get_current_user)
                ): 
    user_query = db.query(models.User).filter(id==models.User.id, logged_user.id==id)
    user_found = user_query.first()
    if not user_found:
        raise HTTPException(
                            status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"User with id '{id}' not found..."
                            )
    user_query.delete(synchronize_session=False)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)

# @router.patch("/")
# def update_field_of_users():
#   return