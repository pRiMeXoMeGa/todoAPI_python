from fastapi import APIRouter, Depends, HTTPException, status, Response
from.. import schemas, models, database, oauth2
from typing import List
from sqlalchemy import func
from sqlalchemy.orm import Session

router = APIRouter(
    prefix="/todos",
    tags=['Todos']
)

@router.get(
            "/", 
            response_model=schemas.TodosOutAll
            )
def get_all_todos(
            db:Session=Depends(database.get_db),
            logged_user:Session = Depends(oauth2.get_current_user)
            ):
    todos = db.query(models.Todo).filter(logged_user.id==models.Todo.user_id).all()
    if not todos:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"No todo list found for user {logged_user.id}")
    return {
            "todos":todos, 
            "user":logged_user
            }



@router.get(
            "/category/{id}", 
            response_model=schemas.TodosOutAll, 
            status_code=status.HTTP_200_OK
            )
def get_todos_category_id(
            id:int, 
            db:Session=Depends(database.get_db),
            logged_user:Session = Depends(oauth2.get_current_user)
            ):
    sharedWith_user_id = db.query(models.ShareTable).filter(
                                                            models.ShareTable.user_id==logged_user.id,
                                                            models.ShareTable.category_id==id
                                                            ).first()
    if not sharedWith_user_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"categoryId {id} not shared with userID {logged_user.id}")
    todos = db.query(models.Todo).filter(id==models.Todo.category).all()
    if todos== None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"no todo list found")
    return {"todos":todos, "user":logged_user}



@router.get(
            "/{id}", 
            response_model=schemas.TodosOutAll,
            status_code=status.HTTP_200_OK
            )
def get_todos_by_todo_id(
            id:int, 
            db:Session=Depends(database.get_db),
            logged_user:Session = Depends(oauth2.get_current_user)
            ):
    todos = db.query(models.Todo).filter(logged_user.id==models.Todo.user_id,
                                         id==models.Todo.id).first()
    if todos== None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"no todo list found")
    return {
            "todos":[todos], 
            "user":logged_user
            }



@router.post(
            "/", 
            response_model=schemas.TodosOut, 
            status_code=status.HTTP_201_CREATED
            )
def create_todos(
            task:schemas.TodosCreate,
            db:Session=Depends(database.get_db),
            logged_user:Session=Depends(oauth2.get_current_user)
            ):
    category = db.query(models.ShareTable.category_id).filter(
                                            models.ShareTable.user_id==logged_user.id,
                                            models.ShareTable.category_id==task.category
                                            ).first()
    if not category:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="user not found")
        
    # category_list_of_logged_user = db.query(models.Category.id).filter(
    #                                         models.Category.user_id==logged_user.id
    #                                         ).all()
    new  = models.Todo(user_id = logged_user.id,**task.dict())
    db.add(new)
    db.commit()
    db.refresh(new)
    return new




@router.put(
            "/{id}", 
            response_model=schemas.TodosOut, 
            status_code=status.HTTP_200_OK
            )
def update_todos(
            id:int, 
            todo:schemas.TodosCreate,
            db:Session=Depends(database.get_db),
            logged_user:Session=Depends(oauth2.get_current_user)
            ):
    sharedWith_user_id = db.query(models.ShareTable).filter(
                                                            models.ShareTable.user_id==logged_user.id,
                                                            models.ShareTable.category_id==todo.category
                                                            ).first()
    if not sharedWith_user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"categoryId {id} not shared with userID {logged_user.id}")
    todo_query = db.query(models.Todo).filter(id == models.Todo.id)
    todos = todo_query.first()
    if not todos:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"record not found or you are not authorized")
    todo_query.update(todo.dict(), synchronize_session=False)
    db.commit()
    return todo_query.first()



@router.delete("/{id}")
def delete_todos(
            id:int, 
            db:Session=Depends(database.get_db),
            logged_user:Session=Depends(oauth2.get_current_user)
            ):
    # todo_query = db.query(models.Todo).filter(logged_user.id==models.Todo.user_id, id == models.Todo.id)
    todo_query = db.query(models.Todo).filter(models.Todo.id==id)
    todo = todo_query.first()
    if not todo:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"record not found or you are not authorized")

    todo_query.delete(synchronize_session=False)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)



# @router.patch("/{id}")
# def update_field_of_todos(id:int, todo:schemas.TodosCreate,
#                             db:Session=Depends(database.get_db),
#                             logged_user:Session=Depends(oauth2.get_current_user)):
#     todo_query=db.query(models.Todo).filter(logged_user.id==models.Todo.user_id, models.Todo.id==id)
#     todos = todo_query.first()
#     if not todos:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
#                             detail=f"todo not found")
    
#     todos_schema = schemas.TodosCreate(todos)
#     update_data = todo.dict(exclude_unset=True)
#     updated_item = todos_schema.copy(update=update_data)
#     todo_query.update(updated_item, synchronize_session=False)
#     db.commit()
#     return todo_query.first()
