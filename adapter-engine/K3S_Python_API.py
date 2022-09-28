from kubernetes import client, config
from kubernetes.client.rest import ApiException
import time
import random
import paho.mqtt.client as paho

## Create pod
def create_pod(v1, pod_name, c_name, image, namespace, requirements, selector_nodes, volumes):
    try:
        podVolumes=[]
        contVolumes=[]
        for volume in volumes:
            volMount=client.V1VolumeMount(name=volume["name"],mount_path=volume["mountPath"],sub_path=volume["subPath"])
            contVolumes.append(volMount)
            configMap=client.V1ConfigMapVolumeSource(name=volume["name"])
            vol=client.V1Volume(name=volume["name"],config_map=configMap)
            podVolumes.append(vol)

        pod=client.V1Pod()
        pod.metadata=client.V1ObjectMeta(name=pod_name)
        requirements=client.V1ResourceRequirements(requests=requirements)
        container=client.V1Container(name=c_name,resources=requirements,image=image,volume_mounts=contVolumes)

        if selector_nodes=="":      ## Create pod without location preferences 
            spec=client.V1PodSpec(containers=[container],volumes=podVolumes)
            pod.spec=spec
            v1.create_namespaced_pod(namespace=namespace,body=pod)
            return verify_pod_creation(v1, pod_name, namespace)
        else:       ## Create pod with location preferences (affinity)
            for selector in selector_nodes:
                s_values=selector_nodes[selector]['values'][0]
                for value in range(1, len(selector_nodes[selector]['values'])): s_values = s_values + ', ' + str(selector_nodes[selector]['values'][value])
                label_selector=selector + ' in (' + s_values + ')'
                if len(v1.list_node(label_selector=label_selector,watch=False).items)>0:
                    selector_req=client.V1NodeSelectorRequirement(key=selector, operator=selector_nodes[selector]['operator'], values=selector_nodes[selector]['values'])
                    selector_req_list=[]
                    selector_req_list.append(selector_req)
                    terms_list=[]
                    terms_list.append(client.V1NodeSelectorTerm(match_expressions=selector_req_list))
                    affinity=client.V1Affinity(node_affinity=client.V1NodeAffinity(required_during_scheduling_ignored_during_execution=client.V1NodeSelector(node_selector_terms=terms_list)))
                    spec=client.V1PodSpec(containers=[container],affinity=affinity,volumes=podVolumes)
                    pod.spec=spec
                    print('creating pod with selectors')
                    v1.create_namespaced_pod(namespace=namespace,body=pod)
                    return verify_pod_creation(v1, pod_name, namespace)
            return ('No nodes available')        ## Return false if there is no node that meets the location preferences
    except ApiException as e:
        print("Exception creating pod: %s\n" % e)
        return e

## Delete pod
def delete_pod(v1, pod_name, namespace):
    try:
        v1.delete_namespaced_pod(pod_name, namespace)
    except ApiException as e:
        print("Exception when calling CoreV1Api->delete_namespaced_pod: %s\n" % e)
    return

## List pods for all namespaces
def list_pods(v1):
    ret = v1.list_pod_for_all_namespaces(watch=False)
    for i in ret.items:
        print("%s\t%s\t%s" % (i.status.pod_ip, i.metadata.namespace, i.metadata.name))
    return

## Return true if pod status is Running and Ready
## Wait 2 minutes if the pod is ContainerCreating status. Then return False if pod status is not Running and Ready
def verify_pod_creation(v1, pod_name, namespace):
    for t in range(6):
        time.sleep(2)
        ret = v1.read_namespaced_pod_status(namespace=namespace, name=pod_name)
        phase = ret.status.phase
        print(phase)
        if (phase=='Running') and (ret.status.container_statuses[0].ready == True):
            print('Running and ready')
            return True
        elif (phase=='Pending') and (ret.status.container_statuses != None):
            if(ret.status.container_statuses[0].state.waiting.reason != 'ContainerCreating'):
                print('Pending and not Container Creating')
                return ('Pending and not Container Creating')
        else:
            print('nor Pending nor Running creatingContainer')
            return ('nor Pending nor Running creatingContainer')
    print('Pending and Container Creating, but exceed 2 minutes')
    return ('Pending and Container Creating, but exceed 2 minutes')

## Offload pod
def offloading_pod(v1, pod_name, image, namespace, requirements, selector_nodes, volumes):
    pod_off_name = pod_name + '-' + str(random.randint(0, 100000))
    respose = create_pod(v1, pod_off_name, pod_off_name, image, namespace, requirements, selector_nodes, volumes)
    if respose == True:
        delete_pod(v1, pod_name, namespace)
        return True
    return respose

## Scale pod
def scaling_pod(v1, instances, image, namespace, requirements, selector_nodes, volumes):
    try:
        pods_ready = 0
        for i in range(int(instances)):
            pod_name = 'pod-0' + str(i) + '-' + str(random.randint(0, 100000))
            response = create_pod(v1, pod_name, pod_name, image, namespace, requirements, selector_nodes, volumes)
            if response == True:
                print('Pod created')
                pods_ready += 1
        if pods_ready == instances:
            return True
        else:
            return ('Scaling error')
    except ApiException as e:
        print("Exception when calling CoreV1Api->create_pod: %s\n" % e)
        return e
    return

## Redeploy pod
def redeployment_pod(v1, pod_name, image, namespace, requirements, selector_nodes, volumes):
    delete_pod(v1, pod_name, namespace)
    i=1
    while (i<24):
        time.sleep(5)
        try:
            ret = v1.read_namespaced_pod_status(namespace=namespace, name=pod_name)
        except ApiException:
            break
        i+=1
    
    try:    
        response = create_pod(v1, pod_name, pod_name, image, namespace, requirements, selector_nodes, volumes)
        if response == True:
            print('Pod redeployed')
            return True
        else:
            return response
    except ApiException as e:
        print("Exception when calling CoreV1Api->delete_namespaced_pod: %s\n" % e)
        return e
    return

## Operate actuator (publishing message in the broker)
def operate_actuator(broker, port, topic, message):
    print(broker)
    print(port)
    print(topic)
    print(message)
    broker = broker
    port = int(port)
    def on_publish(client,userdata,result):             #create function for callback
        print("data published \n")
        pass
    client1= paho.Client("control1")                           #create client object
    client1.on_publish = on_publish                          #assign function to callback
    client1.connect(broker,port)                                 #establish connection
    ret= client1.publish(topic,message)                   #publish
    return True
