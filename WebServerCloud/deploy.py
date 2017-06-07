import fileinput

docker_compose_file = "docker-compose.yml"

def count_start_spaces(string):
    count = 0
    for i in string:
        if i == ' ':
            count += 1
        else:
            return count

def edit_deploy_settings_hostname(hostname):
    for line in fileinput.input(docker_compose_file, inplace=True):
        line = line.replace("\n","")
        if " constraints:" in line:
            print(line.split("[")[0] + "[node.hostname==" + hostname + "]")
        else:
            print(line)
    fileinput.close()

def edit_deploy_settings_mode(mode):    
    for line in fileinput.input(docker_compose_file, inplace=True):
        line = line.replace("\n","")
        if " mode:" in line:
            line.split("mode:")[0]
            print(line.split("mode:")[0] + "mode:", mode)
        elif " constraints:" in line:
            print(line.split("constraints:")[0] + "constraints: [node.role == worker]")
        else:
            print(line)
    fileinput.close()