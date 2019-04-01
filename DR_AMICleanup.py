import boto3
from datetime import datetime
import os

def lambda_handler(event, context):
    
    region_1 = os.environ['DR_Region_name_1']
    region_2 = os.environ['DR_Region_name_2']
    region=[region_1,region_2]
    for reg in region:
        ec2=boto3.client('ec2',region_name = reg)
        now=str(datetime.date(datetime.now()))
        image=ec2.describe_images(Filters=[{'Name':'tag-key','Values':['Delete_On',now]}])
        for imag in image['Images']:
            image_id=imag['ImageId']
            ec2.deregister_image(ImageId=imag['ImageId'])
            snap=ec2.describe_snapshots(Filters=[{'Name':'description','Values':['*'+image_id+'*']}])
            for snapshot in snap['Snapshots']:
                ec2.delete_snapshot(SnapshotId=snapshot['SnapshotId'])
                    
                    
        rds = boto3.client('rds',region_name = reg)
        now=str(datetime.date(datetime.now()))
        response = rds.describe_db_snapshots()
        for snap in response['DBSnapshots']:
            snapshot_arn = snap['DBSnapshotArn']
            snap_tags = rds.list_tags_for_resource(ResourceName=snapshot_arn)
            for tag in snap_tags['TagList']:
                if tag['Key'] == 'Delete_On' and tag['Value']==now :
                    snap_instance=snap['DBSnapshotIdentifier']
                    rds.delete_db_snapshot(DBSnapshotIdentifier=snap_instance)

#ENVIRONMENT VARIABLE :
#DR_Region_name_1
#DR_Region_name_2
                
                    
