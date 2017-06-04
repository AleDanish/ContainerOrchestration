import fileinput
import re
import subprocess

docker_compose_file = "docker-compose.yml"

def count_start_spaces(string):
    count = 0
    for i in string:
        if i == ' ':
            count += 1
        else:
            return count

def edit_deploy_settings(hostname):
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
        elif "node.hostname" in line:
            print(line.split("==")[0] + "==" + hostname)
        else:
            print(line)

def get_swarm_node_list():
    node_list=[]
    cmd="docker node ls | grep Ready | awk '{print $2}'"
    proc = subprocess.Popen((cmd),shell=True, stdout=subprocess.PIPE)
    for line in iter(proc.stdout.readline,''):
        line = line.decode("utf-8")
        if line == '' :
            break
        elif line != '*\n':
            node_list.append(line.rstrip())
    return node_list
