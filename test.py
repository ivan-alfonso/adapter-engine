from os import name
from kubernetes import client, config
from K3S_Python_API import *
import json

config.load_kube_config()

v1 = client.CoreV1Api()
hosts = {'node': {'operator': 'In', 'values': ['edgeNode01','edgeNode02']}, 'layer': {'operator': 'In', 'values': ['fog']}}
pod_name = 'nginx'
namespace = 'default'
requirements = {'memory' : '200Mi', 'cpu' : '200m'}
#result = create_pod(v1, pod_name=pod_name, c_name="mycontainer", image="nginx", namespace=namespace, requirements=requirements, selector_nodes=hosts)
#print (result)
#if result==False:
#   delete_pod(v1, pod_name, namespace)

test=0
for i in range(5):
   test += 1
   print(test)