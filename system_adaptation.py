from kubernetes import client, config
from K3S_Python_API import *
import json

# Configs can be set in Configuration class directly or using helper utility
config.load_incluster_config()
#config.load_kube_config()

v1 = client.CoreV1Api()

def adapt_system(data):
    #print(data)
    adaptations = json.loads(data["alerts"][0]['annotations']['adaptations'])
    print("---------")
    print(data["alerts"][0]['annotations']['adaptations'])
    adapts = data["alerts"][0]['annotations']['adaptations']
    #print(type(adapts))
    status = data["alerts"][0]["status"]
    for adaptation in adaptations:
        print(status)
        print(adaptation)
        if status == 'firing':
            inf=adaptations[adaptation]
            if 'create_pod' in adaptation:
                if create_pod(v1, inf['pod_name'], inf['c_name'], inf['image'], inf['namespace'], inf['requirements'], inf['hosts']) == True:
                    print('Pod created')
            if 'scaling' in adaptation:
                if scaling_pod(v1, inf['instances'], inf['image'], inf['namespace'], inf['requirements'], inf['hosts']) == True:
                    print('Scaling done')
            if 'offloading' in adaptation:
                if offloading_pod(v1, inf['pod_name'], inf['image'], inf['namespace'], inf['requirements'], inf['hosts']) == True:
                    print('offloading done')
                else:
                    print('failed offloading')
            if 'redeployment' in adaptation:
                if redeployment_pod(v1, inf['pod_name'], inf['image'], inf['namespace'], inf['requirements'], inf['hosts']) == True:
                    print('redeployment done')
                else:
                    print('failed redeployment')
            if 'operate_actuator' in adaptation:
                if operate_actuator(inf['broker_ip'], inf['port'], inf['topic'], inf['message']) == True:
                    print('operate actuator done')
                else:
                    print('failed operate actuator')

        else:
            print("estado diferente a firing: )" + data["status"])
    #inf=adaptations[adaptation]
    print("-----------------")
    return
