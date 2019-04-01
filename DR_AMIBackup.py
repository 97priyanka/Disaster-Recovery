import boto3
from datetime import datetime
from datetime import timedelta
import os
import time

def lambda_handler(event, context):
    
    source_region = os.environ['DR_Source_Region_name']
    retention_days = int(os.environ['Retention_Days'])
    deletion_date=str(datetime.date(datetime.now()) + timedelta(days=retention_days))
    
    ec2=boto3.client('ec2',region_name=source_region)
    response = ec2.describe_instances(Filters=[{'Name': 'tag-key', 'Values': ['DR_BACKUP','true']}])
    print("Create ec2 AMI image of all the instances with DR_BACKUP-true")
    for reservation in response["Reservations"]:
        for instance in reservation["Instances"]:
            todays_date=str(datetime.date(datetime.now()))
            ami=ec2.create_image(InstanceId=instance["InstanceId"],Name='AMI-'+instance["InstanceId"]+todays_date,Description='AMI Backup')
            ec2.create_tags(Resources=[ami["ImageId"]],Tags=[{'Key': 'Delete_On','Value': deletion_date}])
    print("Attach the images with tag Delete_On")
            
    rds = boto3.client('rds',region_name=source_region)
    response = rds.describe_db_instances()
    print("Create rds Snapshot of all the instances with DR_BACKUP-true")
    print("Attach the Snapshot with tag Delete_On")
    for db in response['DBInstances']:
        instance_arn = db['DBInstanceArn']
        db_tags = rds.list_tags_for_resource(ResourceName=instance_arn)
        for tag in db_tags['TagList']:
            if tag['Key'] == 'DR_BACKUP' and tag['Value']=='true' :
                db_instance=db['DBInstanceIdentifier']
                now=datetime.now()
                date_time = now.strftime("%d-%m-%Y-%H-%M-%S")
                snap_name=db_instance+date_time
                db_snapshot=rds.create_db_snapshot(DBSnapshotIdentifier=snap_name,DBInstanceIdentifier=db_instance,Tags=[{'Key': 'Delete_On','Value': deletion_date}])

#ENVIRONMENT VARIABLE :
#DR_Source_Region_name
#Retention_Days
    
                    
