import boto3
import json
import os
import io

class s3Bucket:
    def __init__(self):
        self.client = boto3.client('s3')

    def consultS3(self):
        response = self.client.list_buckets()
        i=0
        noone=0
        s3name = str(input("Digite o nome do bucketÇ "))
        while noone == 0:
            names=0
            nonexist=0
            while i < (int(len(response.get('Buckets')))):
                srunning = response.get('Buckets')[i]
                i=i+1
                srunningii = srunning.get('Name')
                if s3name == srunningii:
                    names = names+1
                else:
                    nonexist=nonexist+1
                    names = names+1

            if names == nonexist:
                print(f"Pode aplicar o nome {s3name}.")
                noone=noone+1

            else:
                print('Esse nome já foi utilizado!!')
                s3name = str(input("Por favor, digite outro nome para o bucket: "))
                i=0
                names=0
                nonexist=0
        return s3name


class sS3:
    def __init__(self, bucketname):
        self.bucketname = bucketname
        self.client = boto3.client('s3')

    def createS3(self):
        answer = str(input(f'Deseja mesmo criar o bucket {self.bucketname}? (yes or no)  '))
        if answer == 'yes':
            acl = str(input('Informe o tipo de ACL: private, public-read, public-read-write, authenticated-read '))
            response = self.client.create_bucket(
                ACL=acl,
                Bucket=self.bucketname
            )
            print(f'Bucket {self.bucketname} criado com sucesso!!')
            buckettag = str(input('Agora indique a tag BILLING para este bucket:  '))
            response = self.client.put_bucket_tagging(
                Bucket=self.bucketname,
                Tagging={
                    'TagSet': [
                        {
                            'Key': 'BILLING',
                            'Value': buckettag
                        },
                    ]
                }
            )
            print('Bucket tageado com sucesso!')
        else:
            pass

    def createObject(self):
        foldername = str(input('Digite o nome do folder:  '))
        response = self.client.put_object(
            ACL='bucket-owner-full-control',
            Bucket=self.bucketname,
            Key=foldername
        )
        foldernew = str(input('Deseja criar mais pastas? yes or no'))
        if foldernew == 'yes':
            self.bucketname = sS3(self.bucketname)
            s2 = self.bucketname.createObject()

        else:
            pass

class Policy:
    def __init__(self, bucketname):
        self.bucketname=bucketname
        self.client=boto3.client('iam')

    def policyCreationAllRights(self):
        print('Vamos criar a política de usuário interno!')
        pname = str(input('Digite o nome da policy:   '))
        descrip = str(input('Digite a descrição da política:   '))
        policyDocumentInt = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Sid": "AllowListingOfUserFolder",
                    "Action": [
                        "s3:ListBucket",
                        "s3:GetBucketLocation"
                    ],
                    "Effect": "Allow",
                    "Resource": [
                        f"arn:aws:s3:::{self.bucketname}"
                    ]
                },
                {
                    "Sid": "HomeDirObjectAccess",
                    "Effect": "Allow",
                    "Action": [
                        "s3:PutObject",
                        "s3:GetObject",
                        "s3:DeleteObjectVersion",
                        "s3:DeleteObject",
                        "s3:GetObjectVersion"
                    ],
                    "Resource": f"arn:aws:s3:::{self.bucketname}/*"
                }
            ]
        }
        response = self.client.create_policy(
            PolicyName=f'{pname}-transfer',
            PolicyDocument=json.dumps(policyDocumentInt),
            Description=f'{descrip}'
        )
        pname = f"{pname}-transfer"
        rolecreation = Role(pname)
        rc = rolecreation.roleCreation()
        return pname

    def policyCreationLimitedRights(self):
        print('Vamos criar a política de usuário externo!')
        pname = str(input('Digite o nome da policy:   '))
        descrip = str(input('Digite a descrição da política:   '))
        policyDocumentExt = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Sid": "AllowListingOfUserFolder",
                    "Action": [
                        "s3:ListBucket",
                        "s3:GetBucketLocation"
                    ],
                    "Effect": "Allow",
                    "Resource": [
                        f"arn:aws:s3:::{self.bucketname}"
                    ]
                },
                {
                    "Sid": "AllowReadAMADREFolder",
                    "Effect": "Allow",
                    "Action": [
                        "s3:GetObject",
                        "s3:GetObjectVersion"
                    ],
                    "Resource": f"arn:aws:s3:::{self.bucketname}/*"
                }
            ]
        }
        response = self.client.create_policy(
            PolicyName=f'{pname}-external-transfer',
            PolicyDocument=json.dumps(policyDocumentExt),
            Description=f'{descrip}'
        )
        pname = f"{pname}-external-transfer"
        rolecreation = Role(pname)
        rc = rolecreation.roleCreation()
        return pname

class Role:
    def __init__(self, polname):
        self.polname=polname
        self.client=boto3.client('iam')

    def roleCreation(self):
        roledescription = str(input('Digite a descrição da role:  '))
        tagvalue = str(input('Digite o valor da tag BILLING:  '))
        trustPolicy={
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Principal": {
                    "Service": "s3.amazonaws.com"
                },
                "Action": "sts:AssumeRole"
            },
            {
                "Effect": "Allow",
                "Principal": {
                    "Service": "transfer.amazonaws.com"
                },
                "Action": "sts:AssumeRole"
            }
         ]
        }
        try:
            response = self.client.create_role(
                RoleName=f'{self.polname}-role',
                AssumeRolePolicyDocument=json.dumps(trustPolicy),
                Description=f'{roledescription}',
                Tags=[
                    {
                        'Key': 'BILLING',
                        'Value': f'{tagvalue}'
                    },
                ]
            )
        except self.client.exceptions.MalformedPolicyDocumentException as e:
            print(e)

        response = self.client.attach_role_policy(
            RoleName=f'{self.polname}-role',
            PolicyArn=f'arn:aws:iam::xxxxxxxxxxx:policy/{self.polname}'
        )
        print(response)


def main():
    sname = s3Bucket()
    nameS3Creation = sname.consultS3()
    bucketname = sS3(nameS3Creation)
    s = bucketname.createS3()
    s1 = bucketname.createObject()
    buc = Policy(nameS3Creation)
    poliname = buc.policyCreationAllRights()
    plname = buc.policyCreationLimitedRights()
    print(f'Bucket {nameS3Creation}, policies {poliname}, {plname} e respectivas roles criadas com sucesso!!')

if __name__ == "__main__":
    main()