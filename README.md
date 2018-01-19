#CSM_Cleanup
======================
A project to clean up abandoned snapshots that were created by Dell EMC Cloud Snapshot Manager (aka Amazonite).

## Description
This utility can be used to remove snapshots that were created by Dell EMC Cloud Snapshot Manager (CSM). This may be required if CSM was removed from a cloud account prior to expiring any snapshots.

## Installation

CSM_Cleanup is designed to run as a standalone Python script or as a Lambda script in Amazon Web Services (AWS).

### Staandalone Python

1. Install Python3
  * This script was developed and tested using Python 3.6.4.

2. Install <a href="http://boto3.readthedocs.io/en/latest/guide/quickstart.html#installation">boto3</a>
> pip3 install boto3

3. Setup your ~/.aws/credentials file
  * See the <a href="http://boto3.readthedocs.io/en/latest/guide/quickstart.html#configuration">boto3</a> documentation for more details.

4. Clone or copy the CSM_Cleanup.py script to the directory of your choice.

5. Make CSM_Cleanup.py executable

6. Modify the first line of CSM_Cleanup.py to point to your Python interpreter.

## Usage Instructions
```
usage: CSM_Cleanup.py [-h] [--expire DD] [--regions REGIONS [REGIONS ...]]
                      [--service {EC2,RDS,all}] [--dryrun]

Remove snapshots that were abandoned by Dell EMC Cloud Snapshot Manager (aka Amazonite)

optional arguments:
  -h, --help            show this help message and exit
  --expire DD           expire Dell EMC Cloud Snapshot Manager (aka Amazonite)
                        snapshots older than DD days. Default is 60 days.
  --regions REGIONS [REGIONS ...]
                        AWS regions to search for Dell EMC Cloud Snapshot
                        Manager (aka Amazonite). Default is all regions.
  --service {EC2,RDS,all}
                        Type of snapshot to remove (EC2|RDS|ALL) for Dell EMC
                        Cloud Snapshot Manager (aka Amazonite). Default is all
                        types.
  --dryrun              Dry run only. Do not actually delete snapshots.
                        Default is false.
```

## Future
No updates are planned but anything is possible.

## Contribution
Create a fork of the project into your own repository. Make all your necessary changes and create a pull request with a description on what was added or removed and details explaining the changes in lines of code. If approved, project owners will merge it.

Licensing
---------
Your Project Name is freely distributed under the MIT License. See LICENSE for details.


Support
-------
Please file bugs and issues on the Github issues page for this project. This is to help keep track and document everything related to this repo. For general discussions and further support you can join the <a href="http://community.codedellemc.com/">{code} Community slack channel</a>. The code and documentation are released with no warranties or SLAs and are intended to be supported through a community driven process.
