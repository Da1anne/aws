import boto3
import sys
import datetime
from datetime import date, datetime, timedelta

class iamGroup:
    def __init__(self):
        self.iam = boto3.client('iam')

    def consultIAMGroup(self):
        response = self.iam.get_group(
            GroupName= 'Admins'
        )

        print(f'Members of the Group {response["Group"]["GroupName"]}:')

        count = 0
        user_created = 0
        actual_date = date.today()
        diff = timedelta(days=1)
        last_day_date = actual_date
        last_day_date = last_day_date - diff
        for user in response['Users']:
            print(f'Username: {user['UserName']}\nCreateDate: {user['CreateDate']}\n')
            count = count + 1
            user_creation_date = datetime.strftime(user['CreatedDate'], '%Y-%m-%d')
            if user_creation_date == actual_date or user_creation_date == last_day_date:
                user_created = user_created+1

        print(f'This group contains {count} users.')
        print(f'The number of users added to this group was {user_created}.')

        if user_created > 0:
            finalmessage = 'The group was changed! NEW USER ADDED!'

        elif user_creation_date == 0:
            finalmessage = 'No user added.'

        return finalmessage

def main():
    iam = iamGroup()
    countiamgroup = iam.consultIAMGroup()
    print('Running!!')
    print(countiamgroup)

if __name__ == "__main__":
    main()