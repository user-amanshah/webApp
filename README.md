# AWS (CSYE 6225)

---------------------------------------------------------------

### Summary

This is a  web application Library Management system built with spring
boot and deployed on AWS

-   EC2 instances are built on a custom
    [AMI](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/AMIs.html)
    using [packer](https://packer.io/)
-   Setting up the network and creation of resources is automated with
    Cloud formation, aws cli and shell scripts
-   Instances are autoscaled with
    [ELB](https://aws.amazon.com/elasticloadbalancing/) to handle the
    web traffic
-   Created a [serverless](https://aws.amazon.com/lambda/) application
    to facilitate "pending bills email" using
    [SES](https://aws.amazon.com/ses/) and
    [SNS](https://aws.amazon.com/sns/)
-   The application is deployed with Circle CI and AWS Code Deploy

### Architecture Diagram

 ![aws_full](https://user-images.githubusercontent.com/42703011/92800898-211c7580-f383-11ea-9b4e-76c171fca750.png)


Tools and Technologies
----------------------
                          
| Infrastructure       | VPC, ELB, EC2, Route53, Cloud formation, Shell, Packer |
|----------------------|--------------------------------------------------------|
| Webapp               | Python, FLASK, POSTGRES, Boto3                        |
| CI/CD                | Circle CI, AWS Code Deploy                             |
| Alerting and logging | statsd, CloudWatch, SNS, SES, Lambda                  |
| Security             | WAF                                                    |


Infrastructure-setup
--------------------

-   Create the networking setup using cloud formation and aws cli
-   Create the required IAM policies and users
-   Setup Load Balancers, Route53, DynamoDB, SNS, SES, RDS, WAF

Webapp
------

-   The Bill Management System Web application is developed using
    Python Flask framework that uses the REST architecture
-   Secured the application with [Basic Authentication Security](https://developer.mozilla.org/en-US/docs/Web/HTTP/Authentication)
    to retrieve user information
-   Created pip3 dependencies to run the app locally and when deployed on
    AWS
-   Storing the images of Bill and invoices in S3
-   Generating [Pre-signed
    URL using BOTO3](https://boto3.amazonaws.com/v1/documentation/api/latest/guide/s3-presigned-urls.html)
    to with expiration of 60 minutes


## Build Instructions
Pre-Requisites: Need to have postman installed
-  Clone this repository  into the local system 
-  Go to the folder /webapp
-  Download all pip dependencies by running "pip3 install -r requirements.txt" 
-  Run WebappApplication by typing python3 views.py or user [forever](https://www.npmjs.com/package/forever) manager to run it in backgroung


## Running Tests
- Used python unittest and junit for load testing test case.
- Run WebappApplication test cases:  python3 -m unittest test_app.py


CI/CD
-----

-   Created a webhook from github to CircleCI
-   Bootstrapped the docker container in CircleCI to run the unit tests,
    integration tests and generate the artifact
-   The artifact generated is stored S3 bucket and deployed to an
    autoscaling group. ![ci-cd](https://user-images.githubusercontent.com/42703011/92802596-a7858700-f384-11ea-89db-85f0f8de8bc7.png)


Auto scaling groups
-------------------

-   Created auto scaling groups to scale to the application to handle
    the webtraffic and keep the costs low when traffic is low
-   Created cloud watch alarms to scale up and scale down the EC2
    instances

Serverless computing
--------------------

-   Created a pub/sub system with SNS and lambda function
-   When the user request for a list of url to view pending bills within span of "c" days, send message is published to
    the SNS topic.
-   The lambda function checks for the entry of the emails in DynamoDB if
    it has no entry then it inserts a record with a TTL of 15 minutes
    and sends the notification to the user with SES ![alt
    text]![lambda](https://user-images.githubusercontent.com/42703011/92802718-c126ce80-f384-11ea-843f-a06d1267bdd9.png)


[Packer](https://packer.io/)
----------------------------

-   Implemented CI to build out an AMI and share it between organization
    on AWS
-   Created provisioners and bootstrapped the EC2 instance with required
    tools like FLASK, cloudformation, Python
    
    
## Team Information

| Name | NEU ID | Email Address |
| --- | --- | --- |
| AMAN SHAH| 001059664 | shah.ama@husky.neu.edu|

