import fileinput

docker_compose_file = "docker-compose.yml"

def count_start_spaces(string):
    count = 0
    for i in string:
        if i == ' ':
            count += 1
        else:
            return count

def get_replicas_number():
    f = open(docker_compose_file, "r")
    for line in f.readlines():
        if "replicas:" in line:
            replicas_number = line.split("replicas:")[1].replace("\n","").strip()
            break
    f.close()
    return int(replicas_number)

def edit_deploy_settings_replicas(replicas_num):    
    for line in fileinput.input(docker_compose_file, inplace=True):
        line = line.replace("\n","")
        if " replicas:" in line:
            print(line.split("replicas:")[0] + "replicas: " + str(replicas_num))
        else:
            print(line)
    fileinput.close()

def edit_deploy_settings_mode(mode):    
    for line in fileinput.input(docker_compose_file, inplace=True):
        line = line.replace("\n","")
        if " mode:" in line:
            line.split("mode:")[0]
            print(line.split("mode:")[0] + "mode: " + mode)
        else:
            print(line)
    fileinput.close()
    
def edit_deploy_settings_node_labes(label_key, label_value):
    for line in fileinput.input(docker_compose_file, inplace=True):
        line = line.replace("\n","")
        if " constraints:" in line:
            print(line.split("[")[0] + "[node.labels." + label_key + "==" + label_value + "]")
        else:
            print(line)
    fileinput.close()
