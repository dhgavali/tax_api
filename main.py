from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session

from . import crud, models, schemas
from .database import SessionLocal, engine
from datetime import datetime
import httpx
models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/users/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_user(db=db, user=user)

@app.get("/users/", response_model=list[schemas.User])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = crud.get_users(db, skip=skip, limit=limit)
    return users

@app.get("/users/{user_id}", response_model=schemas.User)
def read_user(user_id: int, db: Session = Depends(get_db)):
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


@app.post("/licenses/", response_model=schemas.License)
def create_license(license: schemas.LicenseCreate, db: Session = Depends(get_db)):
    db_license = crud.get_license(db, refno=license.refno)
    if db_license:
        raise HTTPException(status_code=400, detail="License with this reference number already exists")
    return crud.create_license(db=db, license=license)

@app.get("/licenses/", response_model=list[schemas.License])
def read_licenses(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    licenses = crud.get_licenses(db, skip=skip, limit=limit)
    return licenses

@app.get("/licenses/{refno}", response_model=schemas.License)
def read_license(refno: int, db: Session = Depends(get_db)):
    db_license = crud.get_license(db, refno=refno)
    if db_license is None:
        raise HTTPException(status_code=404, detail="License not found")
    return db_license



@app.get("/getstatus/")
async def get_status(refNo: str, db: Session = Depends(get_db)):
    url = f"https://foscos.fssai.gov.in/gateway/commonauth/commonapi/gettrackapplicationdetails/{refNo}"
    
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail="Failed to fetch data from external API")
        return response.json()  # Return the JSON response from the external API



@app.post("/addLicense/")
async def add_license(refNo: str, db: Session = Depends(get_db)):
    # Fetch status from the external API
    url = f"https://foscos.fssai.gov.in/gateway/commonauth/commonapi/gettrackapplicationdetails/{refNo}"
    
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail="Failed to fetch data from external API")
        
        data = response.json()
        
        if not data or len(data) == 0:
            raise HTTPException(status_code=404, detail="No data found for the provided reference number")
        
        # Extract the first item from the response
        item = data[0]
        
        # Convert 'dd-mm-yyyy' to 'yyyy-mm-dd'
        appSubmissionDate = datetime.strptime(item["appSubmissionDate"], "%d-%m-%Y").date()
        
        # Create a LicenseCreate schema object from the data
        license_data = schemas.LicenseCreate(
            refno=item["refId"],
            client_name=item["companyName"],
            address=item["addressPremises"],
            date=appSubmissionDate,  # Date should be in yyyy-mm-dd format
            status=item["statusDesc"],
            licenseCategoryName=item["licenseCategoryName"],
        )
        
        # Call the create_license function to insert the data
        created_license = crud.create_license(db=db, license=license_data)
        
        return created_license