import boto3

class S3UploadException(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)


class S3Upload(object):
    def __init__(self, access_key, secret_key):
        self.s3 = boto3.resource('s3',aws_access_key_id=access_key, aws_secret_access_key=secret_key)

    def upload(self, src_path, filename, bucket):
        # Lease Bucket como destination path 
        if not src_path.endswith('/'):
            src_path = src_path + '/'

        try:
            with open(src_path +  filename) as f:
                buffer = f.read()

            f.close()
        except Exception as e:
            raise S3UploadException(str(e))

        try:
            self.s3.Bucket(bucket).put_object(Key=filename, Body=buffer)
            return True
        except Exception as e:
            raise S3UploadException(str(e))

