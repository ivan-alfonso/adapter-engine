from kubernetes import client, config
from K3S_Python_API import *
import json
import logging
import time
from datetime import datetime

# Configs can be set in Configuration class directly or using helper utility
config.load_incluster_config()
#config.load_kube_config()

logging.basicConfig(filename="/home/log.txt", level=logging.DEBUG)

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
                logging.debug(str(datetime.now()) + " - starting adaptation: " + str(adaptation))
                response = create_pod(v1, inf['pod_name'], inf['c_name'], inf['image'], inf['namespace'], inf['requirements'], inf['hosts'], inf['volumes'])
                if  response == True:
                    print('Pod created')
                    logging.debug(str(datetime.now()) + " - successful adaptation: " + str(adaptation))
                else:
                    logging.debug(str(datetime.now()) + " - failed adaptation: " + str(adaptation) + " ---- error: " + str(response))
                    print(str(response))
            if 'scaling' in adaptation:
                logging.debug(str(datetime.now()) + " - starting adaptation: " + str(adaptation))
                response = scaling_pod(v1, inf['instances'], inf['image'], inf['namespace'], inf['requirements'], inf['hosts'], inf['volumes'])
                if response == True:
                    print('Scaling done')
                    logging.debug(str(datetime.now()) + " - successful adaptation: " + str(adaptation))
                else:
                    logging.debug(str(datetime.now()) + " - failed adaptation: " + str(adaptation) + " ---- error: " + str(response))
                    print(str(response))
            if 'offloading' in adaptation:
                logging.debug(str(datetime.now()) + " - starting adaptation: " + str(adaptation))
                response = offloading_pod(v1, inf['pod_name'], inf['image'], inf['namespace'], inf['requirements'], inf['hosts'], inf['volumes'])
                if response == True:
                    print('offloading done')
                    logging.debug(str(datetime.now()) + " - successful adaptation: " + str(adaptation))
                else:
                    logging.debug(str(datetime.now()) + " - failed adaptation: " + str(adaptation) + " ---- error: " + str(response))
                    print(str(response))
            if 'redeployment' in adaptation:
                logging.debug(str(datetime.now()) + " - starting adaptation: " + str(adaptation))
                response = redeployment_pod(v1, inf['pod_name'], inf['image'], inf['namespace'], inf['requirements'], inf['hosts'], inf['volumes'])
                if response == True:
                    print('redeployment done')
                    logging.debug(str(datetime.now()) + " - successful adaptation: " + str(adaptation))
                else:
                    logging.debug(str(datetime.now()) + " - failed adaptation: " + str(adaptation) + " ---- error: " + str(response))
                    print(str(response))
            if 'operate_actuator' in adaptation:
                logging.debug(str(datetime.now()) + " - starting adaptation: " + str(adaptation))
                response = operate_actuator(inf['broker_ip'], inf['port'], inf['topic'], inf['message'])
                if response == True:
                    print('operate actuator done')
                    logging.debug(str(datetime.now()) + " - successful adaptation: " + str(adaptation))
                else:
                    logging.debug(str(datetime.now()) + " - failed adaptation: " + str(adaptation) + " ---- error: " + str(response))
                    print(str(response))

        else:
            print("estado diferente a firing: )" + data["status"])
    #inf=adaptations[adaptation]
    print("-----------------")
    return
