import boto3

session = Session(aws_access_key_id="AKIA2O35OSSSLRO7OS4H",aws_secret_access_key="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")

client = session.client('s3' , region_name='us-east-2)
filename='requirement.txt'
object_name = "abch"+"/"+file_name
s3_client = boto3.client('s3')
uploading = s3_client.upload_file(filename, 'amanvpc-s3bucket-wmzxbkinq4uo', 'file.txt')




#uploading = s3_client.upload_file(file.read(), b
# ucket, object_name)

# import boto3
#
s3 = boto3.resource('s3',aws_access_key_id="",aws_secret_ccess_key="")
s3.bucket
BUCKET = "test"

# s3.Bucket(BUCKET).upload_file("your/local/file", "dump/file")