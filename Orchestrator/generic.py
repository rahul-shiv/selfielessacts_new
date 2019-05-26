import os
import docker
import json
import time
import threading
import re
from flask import Flask,request,redirect
import requests
import math
from multiprocessing import Process
from read_xml import xmlReader

app = Flask(__name__)
microservice = {}
SITE_NAME = 'http://localhost:'
portList = []
container_port = dict()
index = 0
countReq = 0
timer = 0 
lock = threading.Lock()

def start_container(tempservice,ports):
    print(tempservice,"hi",ports)
    x = client.containers.run(tempservice["image_name"],detach=tempservice["detach"],ports=ports,mem_limit = tempservice["mem_limit"])
    return x

def timing_func():
    global countReq
    global portList
    global container_port
    global timer
    global microservice
    now = time.time()
    print("Thread started at :"+ str(now))
    while(True):
        if(time.time() - now >= 1):
            poll_container()
            now = time.time()
            print(portList)
        if(timer != 0 and time.time() - timer >= (microservice["time_period"])):
            print("Time up!")
            noOfContainers = len(portList)
            noOfContainersReq = math.ceil((countReq+1)/(microservice["threshold"])) - noOfContainers
            lock.acquire()
            countReq = 0
            lock.release()
            portNo = max(portList)
            if noOfContainersReq < 0 :
                #down
                noOfContainersReq = noOfContainersReq * -1
                print("Remove" , noOfContainersReq)
                for i in range(noOfContainersReq):
                    lock.acquire()
                    container = container_port[str(portNo - i)]
                    print(container)
                    portList.remove(portNo - i)
                    print(portList)
                    lock.release()
                    os.system("docker kill "+ container.id)
                    time.sleep(2)
            elif noOfContainersReq > 0:
                #up
                print("Add",noOfContainersReq)
                for i in range(1,noOfContainersReq + 1):
                    x = start_container(microservice,ports={microservice["port_mapping"][0]:portNo+i})
                    time.sleep(2)
                    lock.acquire()
                    portList.append(portNo + i)
                    container_port[str(portNo + i)] = x
                    lock.release()
            timer = time.time()
    


def poll_container():
    global container_port
    global portList
    global microservice
    for i in portList[:]:
        r = requests.get("http://localhost:"+str(i)+microservice["health_check"])
        if(r.status_code!=200):
            print("Dead",i)
            lock.acquire()
            container = container_port[str(i)]
            print(container)
            portList.remove(i)
            print(portList)
            os.system("docker kill "+ container.id)
            lock.release()
            time.sleep(2)
            x = start_container(microservice,ports={microservice["port_mapping"][0]:i})
            time.sleep(2)
            lock.acquire()
            portList.append(i)
            container_port[str(i)] = x
            print(portList,container_port)
            lock.release()
    return 0

@app.route('/')
def hello_world():
    return 'Flask Dockerized'

@app.route('/<path:path>',methods=['GET','POST',"DELETE"])
def proxy(path):
    global SITE_NAME
    global index
    global portList
    global countReq
    global timer 
    print(path)
    if(len(portList)!=0):
        lock.acquire()
        index = (index + 1)%len(portList)
        SITE_NAME = SITE_NAME + str(portList[index]) +"/"
        lock.release()
        print(SITE_NAME)
    if(microservice["alarm"] == True):
        if(timer == 0):
            print("Timer Started")
            timer = time.time()
        countReq = countReq + 1
    if request.method=='GET':
        x = requests.get(f'{SITE_NAME}{path}').content
        SITE_NAME = "http://localhost:"
        return x
    elif request.method=='POST':
        x = requests.post(f'{SITE_NAME}{path}',json=request.get_json()).content
        SITE_NAME = "http://localhost:"
        return x
    elif request.method=='DELETE':
        x = requests.delete(f'{SITE_NAME}{path}').content
        SITE_NAME = "http://localhost:"
        return x

if __name__ == '__main__':
    #os.system("sh cleanup.sh")
    #os.system("docker run  -d --name mongo -p 27017:27017 -v /home/ubuntu/flaskserver/db/:/data/db mvertes/alpine-mongo")
    time.sleep(1)
    client = docker.from_env()
    xmlReaderObj = xmlReader("sample.xml")
    microservice = xmlReaderObj.microservice
    print(microservice)
    if('database' in microservice):
        start_container(microservice["database"],ports = {microservice["database"]["port_mapping"][0]:microservice["database"]["port_mapping"][1]})
    for i in range(int(microservice["initial_count"])):
        x = start_container(microservice,ports={microservice["port_mapping"][0]:str(int(microservice["port_mapping"][1])+i)})
        portList.append(int(microservice["port_mapping"][1])+i)
        print(portList)
        container_port[str(int(microservice["port_mapping"][1])+i)] = x
    print("Sleeping before Polling")
    time.sleep(5)
    t1 = threading.Thread(target=timing_func)
    t1.start()
    app.run(debug=False,host='0.0.0.0',port=80)

