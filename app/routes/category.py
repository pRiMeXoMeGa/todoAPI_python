from fastapi import APIRouter, Depends, HTTPException, status, Response
from.. import schemas, models, database, oauth2
from. import users
from typing import List
from sqlalchemy import func
from sqlalchemy.orm import Session

router = APIRouter(
    prefix="/category",
    tags=['Category']
)

@router.get("/", 
            response_model=schemas.AllCategoryOut,
            status_code=status.HTTP_200_OK)
def get_all_category(
            db:Session=Depends(database.get_db),
            logged_user:Session = Depends(oauth2.get_current_user)
            ):
    # categories = db.query(models.Todo.category, func.count(models.Todo.id).label("count")).group_by(models.Todo.category).all()
    categoryList = db.query(
                            models.ShareTable.user_id, 
                            models.Category
                            ).join(
                                   models.Category
                                   ).filter(
                                            models.ShareTable.user_id==logged_user.id
                                            ).all()
    cate_list = []
    for cat in categoryList:
        temp_cat = get_category_by_id(cat.Category.id, db, logged_user)
        # list =[]
        # for share in temp_cat.sharedWith:
        #     user = users.get_users(share.user_id, db, logged_user)
        #     list.append(user)
        # temp_cat.sharedWith = list
        cate_list.append(temp_cat)
    
    return {
            "categories":cate_list, 
            "user":logged_user
            }



@router.get(
            "/{id}", 
            response_model=schemas.SharedOut,
            status_code=status.HTTP_200_OK
            )
def get_category_by_id(
            id:int,
            db:Session=Depends(database.get_db),
            logged_user:Session = Depends(oauth2.get_current_user)
            ):
    category = db.query(
                        models.Category
                        ).join(
                               models.ShareTable
                               ).filter(
                                        models.ShareTable.category_id==id,
                                        logged_user.id==models.ShareTable.user_id
                                        ).group_by(
                                                   models.Category.id
                                                   ).first()
    if category==None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"no category found")
    
    if category.isShared == True:
        share_list = db.query(
                              models.ShareTable.user_id
                              ).join(
                                     models.Category
                                     ).filter(
                                              models.ShareTable.category_id==id
                                              ).all()
        if share_list==None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"no user_list found")

        user_list = []
        for user_id in share_list:
            user_details = users.get_users(user_id.user_id, db, logged_user)
            user_list.append(user_details)

        category.sharedWith = user_list
    return category



@router.post(
            "/addUserToCategory",
            response_model=schemas.SharedDataOut,
            status_code=status.HTTP_201_CREATED
            )
def addUserToCategory(
            data:schemas.SharedData, 
            db:Session=Depends(database.get_db),
            logged_user:Session=Depends(oauth2.get_current_user)
            ):
    user_id = db.query(models.User.id).filter(data.user_id==models.User.email).first()
    if not user_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"user does not exist '{data.user_id}'")
    category_name = db.query(
                             models.Category.category
                             ).filter(
                                      models.Category.user_id==logged_user.id, 
                                      models.Category.id==data.category_id
                                      ).first()
    if not category_name:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"category does not exist or category not belong to user - '{data.user_id}'")
    
    duplicate = db.query(
                         models.ShareTable
                         ).filter(
                                  models.ShareTable.user_id==user_id[0],
                                  models.ShareTable.category_id==data.category_id
                                  ).first()
    if duplicate:
        raise HTTPException(status_code=status.HTTP_302_FOUND,
                            detail=f"user - '{data.user_id}' and category - '{category_name[0]}' already exist")
    
    new_entry = models.ShareTable(user_id = user_id[0], category_id = data.category_id)
    db.add(new_entry)
    db.commit()
    db.refresh(new_entry)
    return new_entry



@router.post("/deleteUserFromCategory")
def deleteUserfromCategory(
            data:schemas.SharedData, 
            db:Session=Depends(database.get_db),
            logged_user:Session=Depends(oauth2.get_current_user)
            ):
    user_id = db.query(models.User.id).filter(data.user_id==models.User.email).first()
    if not user_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"user does not exist '{data.user_id}'")
    category_name = db.query(
                             models.Category.category
                             ).filter(
                                      models.Category.user_id==logged_user.id, 
                                      models.Category.id==data.category_id
                                      ).first()
    if not category_name:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"category does not exist or category not belong to user - '{data.user_id}'")
    delete_query = db.query(models.ShareTable).filter(
                                                      models.ShareTable.user_id==user_id[0],
                                                      models.ShareTable.category_id==data.category_id
                                                      )
    data_exist = delete_query.first()
    if not data_exist:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"record not found")
    delete_query.delete(synchronize_session=False)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)



@router.post(
            "/", 
            # response_model=schemas.CategoryOut, 
            status_code=status.HTTP_201_CREATED
            )
def create_category(
            category:schemas.CategoryCreate,
            db:Session=Depends(database.get_db),
            logged_user:Session=Depends(oauth2.get_current_user)
            ):
    if not logged_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="You are not login, Kindly login!!!")
    new_category = category.dict()
    sharedWith = new_category.pop('sharedWith')
    userList = []
    userList.append(logged_user.id)
    while sharedWith != None and sharedWith != []:
        mailId = sharedWith.pop(0)
        id = db.query(models.User.id).filter(models.User.email==mailId).first()
        if not id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                                detail=f"User with Email {mailId} does not exist.")
        userList.append(id[0])
    
    newCategory  = models.Category(user_id = logged_user.id, **new_category)
    db.add(newCategory)
    db.commit()
    db.refresh(newCategory)
    categoryId = newCategory.id
    # users = userList.copy()
    while userList != None and userList != []:
        userId = userList.pop(0)
        new_entry = models.ShareTable(user_id = userId, category_id = categoryId)
        db.add(new_entry)
        db.commit()
        db.refresh(new_entry)

    new = get_category_by_id(categoryId, db, logged_user)
    return new
    


@router.put("/{id}", 
            # response_model=schemas.CategoryOut, 
            status_code=status.HTTP_200_OK)
def update_category(
            id:int, 
            category:schemas.CategoryUpdate,
            db:Session=Depends(database.get_db),
            logged_user:Session=Depends(oauth2.get_current_user)
            ):
    category_query = db.query(
                              models.Category
                              ).filter(
                                       models.Category.user_id==logged_user.id, 
                                       models.Category.id==id)
    category_data = category_query.first()
    if not category_data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"record not found or you are not authorized")
    
    category_query.update(category.dict(), synchronize_session=False)
    db.commit()
    return category_query.first()



@router.delete("/{id}")
def delete_todos(
            id:int, 
            db:Session=Depends(database.get_db),
            logged_user:Session=Depends(oauth2.get_current_user)
            ):
    category_query = db.query(
                              models.Category
                              ).filter(
                                       models.Category.user_id==logged_user.id, 
                                       models.Category.id==id)
    category = category_query.first()
    if not category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"record not found or you are not authorized")

    category_query.delete(synchronize_session=False)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)

