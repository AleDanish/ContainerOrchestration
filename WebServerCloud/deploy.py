import fileinput
import re

docker_compose_file = "docker-compose.yml"

def count_start_spaces(string):
    count = 0
    for i in string:
        if i == ' ':
            count += 1
        else:
            return count

def edit_deploy_settings_hostname(hostname):
    host_number = re.search(r'\d+$', hostname).group(0)
    for line in fileinput.input(docker_compose_file, inplace=True):
        line = line.replace("\n","")
        if count_start_spaces(line) == 2:
            service_name = line.split(':')[0]
            service_number = re.search(r'\d+$', service_name)
            if service_number is not None:
                service_number = service_number.group(0)
                service_name = service_name[:-len(service_number)]
            print(service_name + host_number + ":")
        elif " constraints:" in line:
            print(line.split("]")[0] + ",node.hostname==" + hostname + "]")
        else:
            print(line)

def edit_deploy_settings(mode, hostname):    
    for line in fileinput.input(docker_compose_file, inplace=True):
        line = line.replace("\n","")
        if " mode:" in line:
            line.split("mode:")[0]
            print(line.split("mode:")[0] + "mode:", mode)
        elif " constraints:" in line:
            print(line.split("constraints:")[0] + "constraints: [node.role == worker]")
        else:
            print(line)
    if hostname != None:
        edit_deploy_settings_hostname(hostname)