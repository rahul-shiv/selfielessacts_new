import os
import docker
import json
import time
import threading
import re
from flask import Flask,request,redirect,Response
import requests
import math
from multiprocessing import Process

app = Flask(__name__)
SITE_NAME = 'http://localhost:'
portList = []
container_port = dict()
index = 0
countReq = 0
timer = 0

lock = threading.Lock()

def timing_func():
    global countReq
    global portList
    global container_port
    global timer
    now = time.time()
    print("Thread started at :"+ str(now))
    while(True):
        if(time.time() - now >= 1):
            poll_container()
            now = time.time()
            print(portList)
        if(timer != 0 and time.time() - timer >= 120):
            noOfContainers = len(portList)
            noOfContainersReq = math.ceil((countReq+1)/20) - noOfContainers
            print("120 secs up",countReq,noOfContainersReq)

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
                    portList.remove(portNo - i)
                    lock.release()
                    
                    os.system("docker kill "+ container.id)
                    time.sleep(2)
            elif noOfContainersReq > 0:
                #up
                print("Add",noOfContainersReq)
                for i in range(1,noOfContainersReq + 1):
                    x = client.containers.run('acts',detach=True,ports={'3000/tcp':portNo + i},mem_limit = "128m")
                    time.sleep(2)
                    
                    lock.acquire()
                    portList.append(portNo + i)
                    container_port[str(portNo + i)] = x
                    lock.release()
            
            timer = time.time()



def poll_container():
    global container_port
    global portList
    for i in portList:
        r = requests.get("http://localhost:"+str(i)+"/api/v1/_health")
        if(r.status_code!=200):
            print("Dead",i)
            # remove and kill container
            lock.acquire()
            container = container_port[str(i)]
            portList.remove(i)
            os.system("docker kill "+ container.id)
            lock.release()
            # wait for port to get free
            time.sleep(2)
            x = client.containers.run('acts',detach=True,ports={'3000/tcp':i},mem_limit = "128m")
            time.sleep(2)
            # wait for container to get up and running
            lock.acquire()
            portList.append(i)
            container_port[str(i)] = x
            print(portList,container_port)
            lock.release()
    return 0

@app.route('/')
def hello_world():
    for p in portList:
        print(p)
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
    if(("api/v1" in path) and (("health" not in path) and ("crash" not in path)) ):
        if(timer == 0):
            print("Timer Started")
            timer = time.time()
        countReq = countReq + 1
    if request.method=='GET':
        resp = requests.get(f'{SITE_NAME}{path}')
        SITE_NAME = "http://localhost:"
        excluded_headers = ['content-encoding', 'content-length', 'transfer-encoding', 'connection']
        headers = [(name, value) for (name, value) in resp.raw.headers.items() if name.lower() not in excluded_headers]
        response = Response(resp.content, resp.status_code, headers)
        print(response)
        return response
    elif request.method=='POST':
        resp = requests.post(f'{SITE_NAME}{path}',json=request.get_json())
        SITE_NAME = "http://localhost:"
        excluded_headers = ['content-encoding', 'content-length', 'transfer-encoding', 'connection']
        headers = [(name, value) for (name, value) in resp.raw.headers.items() if name.lower() not in excluded_headers]
        response = Response(resp.content, resp.status_code, headers)
        print(response)
        return response
    elif request.method=='DELETE':
        x = requests.delete(f'{SITE_NAME}{path}').content
        SITE_NAME = "http://localhost:"
        return x

if __name__ == '__main__':
    time.sleep(1)
    client = docker.from_env()
    for i in range(8000,8001):
        x = client.containers.run('acts',detach=True,ports={'3000/tcp':i},mem_limit = "128m")
        portList.append(i)
        print(portList)
        container_port[str(i)] = x
    for x in container_port:
        print(x,container_port[x])
    print("Sleeping before Polling")
    time.sleep(5)
    t1 = threading.Thread(target=timing_func)
    t1.start()
    app.run(debug=False,host='0.0.0.0',port=80)