import boto3
from datetime import datetime
from datetime import timedelta
import os
import time

def lambda_handler(event, context):
    acc_no = os.environ['Account_Number']
    dest_region = os.environ['DR_Destination_Region_name']
    source_region = os.environ['DR_Source_Region_name']
    today=str(datetime.date(datetime.now()))
    ec2=boto3.client('ec2',region_name=source_region)
    imags = ec2.describe_images(Owners=[acc_no])
    for img in imags['Images']:
        for tag in img['Tags']:
            if tag['Key']=='Delete_On':
                deletion_date=tag['Value']
        create_date=img['CreationDate']
        if(create_date.find(today)!=-1):
            ec2 = boto3.client('ec2',region_name=dest_region)
            copy_ami=ec2.copy_image(Name=img['Name'],SourceImageId=img['ImageId'],SourceRegion=source_region)
            ec2.create_tags(Resources=[copy_ami["ImageId"]],Tags=[{'Key': 'Delete_On','Value': deletion_date}])
    print("Migrate the ec2 image from source region to destination region and insert the Delete_On tag")            
            
    rds = boto3.client('rds',region_name=source_region)
    snapshot=rds.describe_db_snapshots()
    for snap in snapshot['DBSnapshots']:
        create_date=str(snap['SnapshotCreateTime'])
        if(create_date.find(today)!=-1):
            db_instance=snap['DBInstanceIdentifier']
            now=datetime.now()
            date_time = now.strftime("%d-%m-%Y-%H-%M-%S")
            snap_name=db_instance+date_time
            rds = boto3.client('rds',region_name=dest_region)
            rds.copy_db_snapshot(SourceDBSnapshotIdentifier= snap['DBSnapshotArn'],TargetDBSnapshotIdentifier=snap_name,SourceRegion=source_region,CopyTags=True)
     print("Migrate the rds snapshot from source region to destination region and insert the Delete_On tag")  

#ENVIRONMENT VARIABLE :
#Account_Number
#DR_Destination_Region_name
#DR_Source_Region_name
                    
