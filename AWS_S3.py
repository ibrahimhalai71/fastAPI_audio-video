import boto3

BUCKET_NAME = "staging-web-capella-audio" 
REGION = "us-east-1"
ACCESS_KEY = "AKIA5B3MF4AFXWZ5I6NE"
SECRET_KEY = "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"

class AWSS3:
    def __init__(self):
        self.s3 = boto3.client(
            service_name='s3',
            region_name= REGION,
            aws_access_key_id= ACCESS_KEY,
            aws_secret_access_key= SECRET_KEY
            )
    
    def upload_file_with_public_access(self, file_path, object_name, bucket_name =BUCKET_NAME):
        try:
            self.s3.upload_file(file_path, bucket_name, object_name)
            self.s3.put_object_acl(ACL='public-read', Bucket=bucket_name, Key=object_name)
            print("File uploaded successfully with public access granted.")
        except Exception as e:
            print("Error uploading file: ", e)

    def put_object_s3(self, file ,key, bucket=BUCKET_NAME ):
        try:
            response = self.s3.put_object(
                # ACL='public-read',
                Body= file,
                Bucket= bucket,
                Key= key
            )
            print("File uploaded successfully with public access granted.")
        except Exception as e:
            print("Error uploading file: ", e)

# Usage
# file_path = "path/to/your/file.mp3"  # Replace with the actual path to your audio/video file
# bucket_name = "your-s3-bucket-name"  # Replace with your S3 bucket name
# object_name = "file.mp3"  # Replace with the desired object name/key in S3

s3_client = AWSS3()
