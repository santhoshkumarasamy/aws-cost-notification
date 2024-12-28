#!/bin/bash


aws cloudformation create-stack --stact-name sns-lambda-pre --template-body ./lambda-template.yaml

aws s3 cp function.zip s3://sns-function-files 

aws cloudformation create-stack --stact-name cost-notification --template-body ./template.yaml
