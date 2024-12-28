import boto3
import os
import datetime
from botocore.exceptions import ClientError

# Initialize AWS Cost Explorer and SNS clients
cost_explorer = boto3.client('ce')
region="us-east-1"
sns = boto3.client('sns', region_name= region)

# SNS topic ARN
#sns_topic_arn = 'arn:aws:sns:ap-south-1:880849992790:CostOptimization'  # Replace with your actual SNS topic ARN
sns_topic_arn = os.environ['SNS_TOPIC']
# Define the Lambda function
def lambda_handler(event, context):
    # Get current date and start of the month
    today = datetime.date.today()
    start_date = today.replace(day=1)
    end_date = today

    try:
        # Query AWS Cost Explorer for cost breakdown per service in ap-south-1 region
        ap_south_1_response = cost_explorer.get_cost_and_usage(
            TimePeriod={
                'Start': start_date.strftime('%Y-%m-%d'),
                'End': end_date.strftime('%Y-%m-%d')
            },
            Granularity='MONTHLY',
            Metrics=['UnblendedCost'],
            GroupBy=[{
                'Type': 'DIMENSION',
                'Key': 'SERVICE'
            }],
            Filter={
                'Dimensions': {
                    'Key': 'REGION',
                    'Values': [ region ]
                }
            }
        )

        # Query AWS Cost Explorer for cost breakdown per service for all regions
        all_regions_response = cost_explorer.get_cost_and_usage(
            TimePeriod={
                'Start': start_date.strftime('%Y-%m-%d'),
                'End': end_date.strftime('%Y-%m-%d')
            },
            Granularity='MONTHLY',
            Metrics=['UnblendedCost'],
            GroupBy=[{
                'Type': 'DIMENSION',
                'Key': 'SERVICE'
            }]
        )

        # Prepare the breakdown of costs for ap-south-1
        ap_south_1_total_cost = 0
        ap_south_1_details = "Cost Breakdown for the us-east-1 Region for the Current Month:\n\n"
        for result in ap_south_1_response['ResultsByTime']:
            for group in result['Groups']:
                service_name = group['Keys'][0]
                cost_amount = float(group['Metrics']['UnblendedCost']['Amount'])
                ap_south_1_total_cost += cost_amount
                ap_south_1_details += f"{service_name}: ${cost_amount:.2f}\n"
        
        ap_south_1_details += f"\nTotal Cost for ap-south-1: ${ap_south_1_total_cost:.2f}\n\n"

        # Prepare the breakdown of costs for all regions
        all_regions_total_cost = 0
        all_regions_details = "Cost Breakdown for All Regions for the Current Month:\n\n"
        for result in all_regions_response['ResultsByTime']:
            for group in result['Groups']:
                service_name = group['Keys'][0]
                cost_amount = float(group['Metrics']['UnblendedCost']['Amount'])
                all_regions_total_cost += cost_amount
                all_regions_details += f"{service_name}: ${cost_amount:.2f}\n"
        
        all_regions_details += f"\nTotal Cost for All Regions: ${all_regions_total_cost:.2f}"

        # Combine both reports (ap-south-1 and all regions) into one message
        full_report = ap_south_1_details + all_regions_details

        # Publish the cost report to SNS
        sns.publish(
            TopicArn=sns_topic_arn,
            Subject='AWS Cost Breakdown Report',
            Message=full_report
        )
        return {
            'statusCode': 200,
            'body': 'Cost report for us-east-1 and all regions sent successfully via SNS!'
        }

    except ClientError as e:
        print(f"Error: {e}")
        return {
            'statusCode': 500,
            'body': f"Failed to send cost report: {e}"
        }
