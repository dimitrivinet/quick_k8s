from fastapi import FastAPI, Depends, File, UploadFile
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

app = FastAPI()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


@app.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    # user_dict = fake_users_db.get(form_data.username)
    # if not user_dict:
    #     raise HTTPException(status_code=400, detail="Incorrect username or password")
    # user = UserInDB(**user_dict)
    # hashed_password = fake_hash_password(form_data.password)
    # if not hashed_password == user.hashed_password:
    #     raise HTTPException(status_code=400, detail="Incorrect username or password")

    print(form_data)

    return {"access_token": "dummy_token", "token_type": "bearer"}


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.post("/config")
async def set_config(fileb: UploadFile = File(...),
                     token: str = Depends(oauth2_scheme)
                     ):
    file_bytes = fileb.file.read()
    file_size = len(file_bytes)
    file_as_str = file_bytes.decode("utf-8")

    print(file_as_str)

    return {
        "file_size": file_size,
        "token": token,
        "file_content": file_as_str
    }
