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

def get_swarm_node_list():
    node_list=[]
    #cmd="docker node ls | grep Ready | awk '{print $2}'"
    cmd="docker node ls | awk '{print $2}'"
    proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
    line_number = 0
    for line in iter(proc.stdout.readline,''):
        line_number+=1 
        line = line.decode("utf-8")
        if line == '' :
            break
        elif (line != '*\n') and (line_number > 1): #not consider this node (cloud-leader-manager) and the columns title
            node_list.append(line.rstrip())
    return node_list

def create_services(app_name):
    cmd="docker stack deploy --with-registry-auth --compose-file=" + docker_compose_file + " " + app_name
    subprocess.Popen(cmd, shell=True)
    
def get_token():
    cmd = "docker swarm join-token -q worker"
    proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
    for line in iter(proc.stdout.readline,''):
        return line.decode("utf-8")
    
def ip_from_hostname():
    cmd = "docker node inspect mnip7hymkp6d9b7k099za7rs9 | grep Addr"
    proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
    for line in iter(proc.stdout.readline,''):
        return line.decode("utf-8")
    
