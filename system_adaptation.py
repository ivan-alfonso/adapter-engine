from kubernetes import client, config
from K3S_Python_API import *
import json

# Configs can be set in Configuration class directly or using helper utility
config.load_incluster_config()
#config.load_kube_config()

v1 = client.CoreV1Api()

def adapt_system(data):
    adaptations = json.loads(data["alerts"][0]['annotations']['adaptations'])
    for adaptation in adaptations:
        print(data["status"])
        print(adaptation)
        if data["status"] == 'firing':
            inf=adaptations[adaptation]
            if adaptation == 'create_pod':
                if create_pod(v1, inf['pod_name'], inf['c_name'], inf['image'], inf['namespace'], inf['requirements'], inf['hosts']) == True:
                    print('Pod created')
            if adaptation == 'scaling':
                if scaling_pod(v1, inf['instances'], inf['image'], inf['namespace'], inf['requirements'], inf['hosts']) == True:
                    print('Scaling done')
            if adaptation == 'offloading':
                if offloading_pod(v1, inf['pod_name'], inf['image'], inf['namespace'], inf['requirements'], inf['hosts']) == True:
                    print('offloading done')
                else:
                    print('failed offloading')
            if adaptation == 'redeployment':
                list_pods(v1)
                print('redeploy')
            if adaptation == 'operate_actuator':
                if operate_actuator(inf['broker_ip'], inf['port'], inf['topic'], inf['message']) == True:
                    print('operate actuator done')
                else:
                    print('failed operate actuator')

        else:
            print("estado diferente a firing: )" + data["status"])
    inf=adaptations[adaptation]
    return
