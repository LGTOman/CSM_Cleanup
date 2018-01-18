#!/usr/local/bin/python3

import sys

import boto3
from botocore.exceptions import ClientError, EndpointConnectionError
from datetime import datetime, timedelta, timezone
import argparse
import pprint

product = "Dell EMC Cloud Snapshot Manager (aka Amazonite)"
defaultdays = 60
dryrun = False

parser = argparse.ArgumentParser(description='Remove snapshots that were abandoned by {product}'.format(product=product))
parser.add_argument('--expire', metavar='DD', type=int, default=defaultdays,
                    help='expire {product} snapshots older than DD days. Default is {defaultdays} days.'.format(
                        product=product,
                        defaultdays=defaultdays,
                    ))
parser.add_argument('--regions', action='store', nargs='+', default=['all'],
                    help='AWS regions to search for {product}. Default is all regions.'.format(product=product))
parser.add_argument('--service', action='store', default='all', choices=['EC2', 'RDS', 'all'],
                    help='Type of snapshot to remove (EC2|RDS|ALL) for {product}. Default is all types.'.format(product=product))
parser.add_argument('--dryrun', action='store_true',
                    help='Dry run only. Do not actually delete snapshots. Default is false.')

args = parser.parse_args()
days = args.expire
dryrun = args.dryrun
service = args.service
delete_time = datetime.now(timezone.utc) - timedelta(days=days)

filters = [{'Name':'tag:source', 'Values':['amazonite']}]

sumnum = {}
sumsize = {}

print ('Deleting any snapshots older than {days} days'.format(days=days))

def delsnap_ec2 (days, region) :
    print ('Deleting {product} snapshots in region {region}'.format(
        region=region,
        product=product,
    ))
    try :
        ec2client = boto3.client('ec2', region_name=region)

    except ClientError as err:
        print ('Unable to access the {region} region.'.format(region=region))
        print ("Error: {0}".format(err))
        sumnum[region] = 'N/A'
        sumsize[region] = 'N/A'
        return

    try :
        ec2snapshots = ec2client.describe_snapshots(Filters=filters)['Snapshots']

    except EndpointConnectionError as err:
        print ('Unable to access the {region} region.'.format(region=region))
        print ("Error: {0}".format(err))
        sumnum[region] = 'N/A'
        sumsize[region] = 'N/A'
        return

    deletion_counter = 0
    size_counter = 0

    for ec2snapshot in ec2snapshots:
        start_time = ec2snapshot['StartTime']

        if start_time < delete_time:
            print ('Deleting {description} snapshot: {id}, created on {start_time} of size {volume_size} GB in {region}'.format(
                id=ec2snapshot['SnapshotId'],
                start_time=ec2snapshot['StartTime'],
                volume_size=ec2snapshot['VolumeSize'],
                description=ec2snapshot['Description'],
                region=region,
            ))
            # Just to make sure you're reading!
            ec2 = boto3.resource('ec2', region_name=region)
            ec2snap = ec2.Snapshot(ec2snapshot['SnapshotId'])

            try:

                ec2response = ec2snap.delete(
                    DryRun=dryrun
                )

                deletion_counter = deletion_counter + 1
                size_counter = size_counter + ec2snapshot['VolumeSize']

            except ClientError as err:
                print ('Unable to delete snapshot {snapshot}.'.format(snapshot=ec2snapshot['SnapshotId']))
                print ("Error: {0}".format(err))
                #return

    print ('Deleted {number} snapshots totalling {size} GB in region {region}'.format(
        number=deletion_counter,
        size=size_counter,
        region=region,
    ))


    sumnum[region] = deletion_counter
    sumsize[region] = size_counter

def delsnap_rds (days, region) :
    print ('Deleting {product} snapshots in region {region}'.format(
        region=region,
        product=product,
    ))

    rdsclient = boto3.client('rds', region_name=region)

    try :
        rdssnapshots = rdsclient.describe_db_snapshots()['DBSnapshots']

    except EndpointConnectionError as err:
        print ('Unable to access the {region} region.'.format(region=region))
        print ("Error: {0}".format(err))
        sumnum[region] = 'N/A'
        sumsize[region] = 'N/A'
        return

    deletion_counter = 0
    size_counter = 0

    for rdssnapshot in rdssnapshots:
        #start_time = datetime.strptime(
        #     rdssnapshot['SnapshotCreateTime'],
        #     '%Y-%m-%dT%H:%M:%S.000Z'
        #)
        start_time = rdssnapshot['SnapshotCreateTime']

        if start_time < delete_time and (
            rdssnapshot['DBSnapshotIdentifier'].startswith('cloud-snapshot-manager-') or
            rdssnapshot['DBSnapshotIdentifier'].startswith('amazonite-snapshot-')
        ):
            print ('Deleting {engine} database {dbname} snapshot: {id}, created on {start_time} of size {volume_size} GB in {region}'.format(
                id=rdssnapshot['DBSnapshotIdentifier'],
                start_time=rdssnapshot['SnapshotCreateTime'],
                volume_size=rdssnapshot['AllocatedStorage'],
                engine=rdssnapshot['Engine'],
                dbname=rdssnapshot['DBInstanceIdentifier'],
                region=region,
            ))
            deletion_counter = deletion_counter + 1
            size_counter = size_counter + rdssnapshot['AllocatedStorage']
            # Just to make sure you're reading!
            if not dryrun:
                rdsresponse = rdsclient.delete_db_snapshot(
                    DBSnapshotIdentifier=rdssnapshot['DBSnapshotIdentifier']
                )

    print ('Deleted {number} snapshots totalling {size} GB in region {region}'.format(
        number=deletion_counter,
        size=size_counter,
        region=region,
    ))


    sumnum[region] = deletion_counter
    sumsize[region] = size_counter

if (service == 'EC2') or (service == 'all') :
    if 'all' in args.regions :
        regions = sorted([r.name for r in ec2.regions()])
    else :
        regions = sorted(args.regions)

    for region in regions :
        delsnap_ec2 (days,region)

        print ()
        print ('Summary of EC2 removals:')

    for region in regions :
        print ('Deleted {number} snapshots totalling {size} GB in region {region}'.format(
            number=sumnum[region],
            size=sumsize[region],
            region=region,
            ))

if (service == 'RDS') or (service == 'all') :

    if 'all' in args.regions :
        regions = sorted([r.name for r in rds.regions()])
    else :
        regions = sorted(args.regions)

    for region in regions :
        delsnap_rds (days,region)

    print ()
    print ('Summary of RDS removals:')

    for region in regions :
        print ('Deleted {number} snapshots totaling {size} GB in region {region}'.format(
            number=sumnum[region],
            size=sumsize[region],
            region=region,
            ))
