from fastapi import FastAPI,HTTPException,Request,Form, File, UploadFile,Header
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os
import boto3
import botocore.exceptions
from starlette.concurrency import run_in_threadpool
from pydantic import BaseModel
from database import SessionLocal,Gallery

app = FastAPI(title="My FastAPI Project")

password_hash=None

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

load_dotenv()

AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_REGION = os.getenv("AWS_REGION")
S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME")

# Initalize S3 Client

s3_client = boto3.client(
    "s3",
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name=AWS_REGION,
)

db= SessionLocal()


# async def uploadimage_to_aws(s3client,S3_BUCKET_NAME,product_img):
#         file_content = await product_img.read()
#         file_key = f"buildberg/{product_img.filename}"
#         s3client.put_object(
#                 Bucket=S3_BUCKET_NAME,
#                 Key=file_key,
#                 Body=file_content,
#                 ContentType=product_img.content_type,
#             )
#         file_url = f"https://{S3_BUCKET_NAME}.s3.{s3_client.meta.region_name}.amazonaws.com/{file_key}"
#         return file_url


async def uploadimage_to_aws(s3client, S3_BUCKET_NAME, product_img):
    try:
        # Read file content asynchronously
        file_content = await product_img.read()
        file_key = f"buildberg/{product_img.filename}"

        await run_in_threadpool(
            s3client.put_object,
            Bucket=S3_BUCKET_NAME,
            Key=file_key,
            Body=file_content,
            ContentType=product_img.content_type,
            ACL="public-read"
        )
        region = s3client.meta.region_name
        file_url = f"https://{S3_BUCKET_NAME}.s3.{region}.amazonaws.com/{file_key}"
        return file_url

    except botocore.exceptions.BotoCoreError as e:
        print(f"❌ Boto3 core error: {e}")
    except botocore.exceptions.ClientError as e:
        print(f"❌ AWS client error: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
    return None


# async def delete_img_from_aws(s3client,S3_BUCKET_NAME,filename):
#     try:
#         file_name = file_name.split("/")[-1]
#         file_name=f"buildberg/{file_name}"
#         s3client.delete_object(Bucket=S3_BUCKET_NAME, Key=filename)
#         return True
#     except Exception as e:
#         return False

async def delete_img_from_aws(s3client, S3_BUCKET_NAME, filename):
    try:
        # Extract just the file name
        file_key = filename.split("/")[-1]
        file_key = f"buildberg/{file_key}"

        # Run the delete_object call in FastAPI's threadpool
        await run_in_threadpool(
            s3client.delete_object,
            Bucket=S3_BUCKET_NAME,
            Key=file_key
        )

        return True

    except botocore.exceptions.ClientError as e:
        print(f"❌ AWS client error: {e}")
    except botocore.exceptions.BotoCoreError as e:
        print(f"❌ Boto3 core error: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
    
    return False


@app.get("/")
async def root():
    return {"message": "Hello, FastAPI!"}


@app.post("/upload_image/")
async def upload_image(
    site_name: str = Form(...),
    client_name: str = Form(...),
    building_square_feet: float = Form(...),
    product_img: UploadFile = File(...)
    ): 
    #filename=await uploadimage_to_aws(s3_client,S3_BUCKET_NAME,product_img)
    #print("aws file url:",filename)
    print(site_name)
    print(client_name)
    print(building_square_feet)
    print(product_img.filename)

    try:
        new_gallery = Gallery(
        site=site_name,
        square_feet=building_square_feet,
        name=client_name,
        image_url=product_img.filename
        )
        db.add(new_gallery)
        db.commit()
        db.refresh(new_gallery)
        print("Inserted User ID:", new_gallery.id)

    except Exception as e:
        db.rollback()  # Rollback if there's an error
        raise HTTPException(status_code=401, detail=f"Error inserting user:{ e}")

    finally:
        db.close()  # Always close the session

    return {"message": f"gallery_id:{new_gallery.id}"}


class AdminLoginRequest(BaseModel):
    username: str
    password: str


from utils import Hashing

@app.post("/adminlogin/")
async def adminlogin(data:AdminLoginRequest):
    global password_hash
    username = data.username
    password = data.password
    if username != os.getenv("admin_username") or password != os.getenv("admin_password"):
        raise HTTPException(status_code=401, detail="Invalid_credentials")

    hashed=await Hashing.hash_password(password)
    password_hash=hashed
    return {"message": "Login successful", "hash": hashed }


@app.get("/gethash")
async def gethash():
    global password_hash
    return {"hash": password_hash}


from utils import Auhtentication
@app.post("/validate_token/")
async def validate_token(authorization: str = Header(None)):
    global password_hash
    result=await Auhtentication(authorization,password_hash)
    return result


@app.get("/gethash")
async def gethash():
    global password_hash
    return {"hash": password_hash}


@app.get("/getgallery/")
async def getgallery():
    try:
        galleries = db.query(Gallery).all()
        print(galleries[0])
        print(f"type:{type(galleries[0])}")
        gallery_data=[]
        for gallery in galleries:
            d= {"id": gallery.id,"name": gallery.name,"site": gallery.site,"square_feet": gallery.square_feet,"image_url": gallery.image_url
            }
            gallery_data.append(d)
            # print(f"ID: {gallery.id}, Name: {gallery.name}, Site: {gallery.site}, Sqft: {gallery.square_feet}, Image URL: {gallery.image_url}")

    except Exception as e:
        print("Error:", e)

    finally:
        db.close()

    return {"message": f"gallery:{gallery_data}"}