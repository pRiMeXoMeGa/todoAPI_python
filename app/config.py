from pydantic import BaseSettings


# pydantic helps in creating a strict schemas for Environment variables using 'BaseSettings class'
class Settings(BaseSettings):
    # setting variables of env variable to proper types
    database_hostname:str
    database_port:str
    database_password:str
    database_name:str
    database_username:str
    secret_key:str
    algorithm:str
    access_token_expire_minutes:int

    # setting the path of envirnment variable file to declare the path of the "env file"
    class Config:
        env_file = ".env"

# creating object of Settings class
settings = Settings()