from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm
from .. import database, schemas, models, utils, oauth2


router = APIRouter(tags=['Authentication'])

@router.get("/verifyToken", response_model=bool)
def verifyToken(logged_user:Session=Depends(oauth2.get_current_user)):
    return True

@router.post("/login", response_model=schemas.Token)
def login(userCredential: OAuth2PasswordRequestForm=Depends(), 
            db:Session=Depends(database.get_db)):
    user = db.query(models.User).filter(
                    models.User.email == userCredential.username
                    ).first()

    if not user:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid Credentials")

    if not utils.verify(userCredential.password, user.password):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid Credentials")

    access_token = oauth2.create_access_token(data={"user_id":user.id})
    
    return {"access_token":access_token, 
            "token_type":"Bearer",
            "user":user}


