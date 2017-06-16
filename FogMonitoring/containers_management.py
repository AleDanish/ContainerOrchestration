#     Author: Alessandro Zanni
#     <alessandro.zanni3@unibo.it>

import subprocess

def delete_exited_containers():
    cmd = "docker ps -a | grep Exit | cut -d ' ' -f 1 | xargs sudo docker rm"
    proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
    for line in iter(proc.stdout.readline,''):
        line = line.decode("utf-8").replace("\n","")
        print(line)
        if line is "":
            break