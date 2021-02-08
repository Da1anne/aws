import boto3
import json

class recursoEscolhido:
    def __init__(self, resource_name, pagToken, num_recursos):
        self.client = boto3.client('resourcegroupstaggingapi')
        self.resource_name = resource_name
        self.pagToken = pagToken
        self.num_recursos = num_recursos

    def escolhaRecurso(self):
        billing = 'BILLING'
        response = self.client.get_resources(
            PaginationToken=f'{self.pagToken}'
            ResourceTypeFilters=[
                f'{self.resource_name}'
            ]
        )
        print(response)
        i=0
        while i < (int(len(response.get('ResourceTagMappingList')))):
            rarn = response.get('ResourceTagMappingList')[i]
            finalArn = rarn.get('ResourceARN')
            print(f'\nANALISANDO O RECURSO {finalArn}')
            self.num_recursos = self.num_recursos + 1
            tag = rarn.get('Tags')
            i = i + 1
            print(tag)
            print('Verificando se tem a TAG ou não.........')
            j = 0
            c = 0
            if tag == []:
                print('SEM TAG BILLING!')
                finalArn = str(finalArn)
                finalArn = finalArn.replace("'",'')
                print(f'O recurso {finalArn} precisa ser tageado.')
                tag_value = 'UNKNOWN'
                tag_obj = Tagging(tag_value, finalArn)
                tag_met = tag_obj.creatingTag()
            else:
                for k, v in tag:
                    if tag[j].get('Key') == billing:
                        j=j+1
                        print("Recurso já possui a TAG BILLING.")
                    else:
                        j = j+1
                        c = c+1
                        if j == len(tag) and c == j:
                            print('SEM TAG BILLING!!')
                            finalArn = str(finalArn)
                            finalArn = finalArn.replace("'",'')
                            print(f'O recurso {finalArn} precisa ser tageado.')
                            tag_value = 'UNKNOWN'
                            tag_obj = Tagging(tag_value, finalArn)
                            tag_met = tag_obj.creatingTag()
        pagToken = str(response.get('PaginationToken'))
        vazio = ''
        if pagToken != vazio:
            print(pagToken)
            rec = recursoEscolhido(self.resource_name, pagToken, self.num_recursos)
            again = rec.escolhaRecurso()
        else:
            print(f'\nO número total de recursos escaneados foi de {self.num_recursos}.')

class Tagging:
    def __init__(self, tag_value, finalArn):
        self.tag_key='BILLING'
        self.tag_value = tag_value
        self.finalArn=finalArn
        self.client=boto3.client('resourcegroupstaggingapi')

    def creatingTag(self):
        response = self.client.tag_resources(
            ResourceARNList=[
                self.finalArn,
            ],
            Tags={
                self.tag_key: self.tag_value
            }
        )
        print('TAG aplicada com sucesso!')

class Todos:
    def __init__(self):
        self.client=boto3.client('config')


    def contandoTodos(self):
        response = self.client.get_discovered_resource_counts(
            limit=100,
            nextToken=''
        )
        cont = response.get('totalDiscoveredResources')
        print(f'O número total de recursos nesta conta AWS é de {cont} recursos.')
        print(response)

def main():
    resource_name= ""
    pagToken= ''
    num_recursos = 0
    resc = recursoEscolhido(resource_name, pagToken, num_recursos)
    r = resc.escolhaRecurso()
    tod = Todos()
    t=tod.contandoTodos

if __name__ == "__main__":
    main()