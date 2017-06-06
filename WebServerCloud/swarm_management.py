import subprocess

docker_compose_file = "docker-compose.yml"

def get_swarm_node_list():
    node_list=[]
    cmd="docker node ls | grep Down | awk '{print $2}'" #consider only the node outside the swarm
    #cmd="docker node ls | awk '{print $2}'"
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
        return line.decode("utf-8").replace("\n","")

def id_from_hostname(hostname):
    cmd1 = "docker node ls | grep " + hostname + "| awk '{print $1}'"
    proc = subprocess.Popen(cmd1, shell=True, stdout=subprocess.PIPE)
    for line in iter(proc.stdout.readline,''):
        return line.decode("utf-8").replace("\n","").strip()

def ip_from_id(host_id):
    cmd = "docker node inspect " + host_id + " | grep Addr"
    proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
    for line in iter(proc.stdout.readline,''):
        line = line.decode("utf-8").replace("\n","").replace("\"","").split("Addr:")[1]
        return line.strip()
    

def remove_node_from_id(host_id):
    cmd = "docker node rm " + host_id
    subprocess.Popen(cmd, shell=True)
