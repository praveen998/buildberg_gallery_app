from fastapi import FastAPI,HTTPException,Request,Form, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os
import boto3

app = FastAPI(title="My FastAPI Project")
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

async def uploadimage_to_aws(s3client,S3_BUCKET_NAME,product_img):
        file_content = await product_img.read()
        file_key = f"hhhperfumes/{product_img.filename}"

        s3client.put_object(
                Bucket=S3_BUCKET_NAME,
                Key=file_key,
                Body=file_content,
                ContentType=product_img.content_type,
            )
        file_url = f"https://{S3_BUCKET_NAME}.s3.{s3_client.meta.region_name}.amazonaws.com/{file_key}"
        return file_url


async def delete_img_from_aws(s3client,S3_BUCKET_NAME,filename):
    try:
        file_name = file_name.split("/")[-1]
        file_name=f"hhhperfumes/{file_name}"
        s3client.delete_object(Bucket=S3_BUCKET_NAME, Key=filename)
        return True
    except Exception as e:
        return False


@app.get("/")
async def root():
    return {"message": "Hello, FastAPI!"}




@app.post("/add_new_product/")
async def add_product(
    product_name: str = Form(...),
    india_price: float = Form(...),
    uae_price: float = Form(...),
    category: str = Form(...),
    product_img: UploadFile = File(...)
): 
    print("product file name:",product_img)
    filename=await uploadimage_to_aws(s3_client,S3_BUCKET_NAME,product_img)
    print("aws file url:",filename)
    product={
        "product_name": product_name,
        "product_description": product_description,
        "product_price": {
            "India": india_price,
            "UAE": uae_price
        },
        "category": category,
        "product_image_url": filename
    }

    return {"message": "image inserted"}
