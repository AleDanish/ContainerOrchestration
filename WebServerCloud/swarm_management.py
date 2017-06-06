import subprocess

docker_compose_file = "docker-compose.yml"

def get_swarm_node_list(status):
    node_list=[]
    cmd="docker node ls | grep " + status + " | awk '{print $2}'" #consider only the node outside the swarm
    #cmd="docker node ls | awk '{print $2}'"
    proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
    for line in iter(proc.stdout.readline,''):
        line = line.decode("utf-8")
        if line == '' :
            break
        elif (line != '*\n'): #not consider this node (cloud-leader-manager) and the columns title
            node_list.append(line.rstrip())
    return node_list

def create_services(app_name):
    cmd="docker stack deploy --with-registry-auth --compose-file=" + docker_compose_file + " " + app_name
    proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
    for line in iter(proc.stdout.readline,''):
        line = line.decode("utf-8").replace("\n","")
        print(line)
        if line is "":
            break
    
def get_token():
    cmd = "docker swarm join-token -q worker"
    proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
    for line in iter(proc.stdout.readline,''):
        return line.decode("utf-8").replace("\n","")

def id_from_hostname(hostname):
    cmd = "docker node ls | grep " + hostname + "| awk '{print $1}'"
    proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
    for line in iter(proc.stdout.readline,''):
        return line.decode("utf-8").replace("\n","").strip()

def ip_from_id(host_id):
    cmd = "docker node inspect " + host_id + " | grep Addr"
    proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
    for line in iter(proc.stdout.readline,''):
        line = line.decode("utf-8").replace("\n","").replace("\"","").split("Addr:")[1]
        return line.strip()
    
def remove_node_from_id(host_id, option):
    cmd = "docker node rm " + option + " " + host_id
    subprocess.Popen(cmd, shell=True)
    
def set_availability_node(host_id, availability_type):
    cmd = "docker node update --availability " + availability_type + " " + host_id
    subprocess.Popen(cmd, shell=True)
