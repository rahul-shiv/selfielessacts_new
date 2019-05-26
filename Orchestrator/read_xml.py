from xml.etree import ElementTree

class xmlReader:
	def __init__(self,path):
		tree = ElementTree.parse(path)
		root = tree.getroot()
		ms = root.find("microservice")
		microservice = {}
		microservice = self.extract_startup_info(ms)
		if(ms.find("initial_count") != None):
			microservice["initial_count"] = ms.find("initial_count").text
		else:
			microservice["initial_count"] = 1

		if(ms.find("health_check") != None):
			microservice["health_check"] = ms.find("health_check").text
		else:
			microservice["health_check"] = "/"
		alarm = ms.find("alarm")
		if(alarm != None):
			microservice["alarm"] = True
			microservice["func"] = alarm.find("func").text
			microservice["threshold"] = int(alarm.find("threshold").text)
			microservice["time_period"] = int(alarm.find("time_period").text)
		else:
			microservice["alarm"] = false
		if(root.find("database") != None):
			microservice["database"] = self.extract_startup_info(root.find("database"))

		self.microservice = microservice

	def extract_startup_info(self,ms):
			tempservice = {}
			if(ms.find("image_name") != None):
				tempservice["image_name"] = ms.find("image_name").text
			elif(ms.find("docker_file") != None):
				# go build and put image name here
				print("use docker")
			else:
				print("Image Name is required!")
			if(ms.find("detach") != None):
				tempservice["detach"] = ms.find("detach").text
			else:
				tempservice["detach"] = true
			if(ms.find("port_mapping") != None):
				tempservice["port_mapping"] = ms.find("port_mapping").text.split(":")
			else:
				print("port mapping is required to set up microservice!")
			if(ms.find("mem_limit") != None):
				tempservice["mem_limit"] = ms.find("mem_limit").text + "m"
			else:
				tempservice["mem_limit"] = "1024m"
			return tempservice
