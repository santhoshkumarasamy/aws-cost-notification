# Setup Monthly cost notification

This help you setup a monthly sns notfication on AWS spendings

Services Used
1. SNS
2. S3
3. Lambda function
4. Eventbridge
5. CloudWatch logs
6. IAM - Role


This is repo is basically IAC version of the below post.
https://towardsaws.com/automating-aws-cost-reporting-with-lambda-and-sns-95222e353b58

```sh
chmod u+x deploy.sh
./deploy.sh
```
Two stacks will be created, one for the pre-requisites and the main one which deploys all the functionalities.
