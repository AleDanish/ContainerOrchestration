import subprocess
import ast

WEB_SERVER_PORT="8889"
WEB_SERVER_IP="192.168.56.101"

def send(hostname, mode, v=None, u=None, filename=None):
    cmd="curl http://" + WEB_SERVER_IP + ":" + WEB_SERVER_PORT + " -F mode=" + mode + " -F hostname=" + hostname
    if filename is not None:
        cmd+=" -F file=@"+filename
    elif (v is not None) and (u is not None):
        cmd += " -F v0=" + str(v[0]) + " -F v1=" + str(v[1]) + " -F v2=" + str(v[2]) + " -F u0=" + str(u[0]) + " -F u1=" + str(u[1]) + " -F u2=" + str(u[2]) 
    proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
    for line in iter(proc.stdout.readline,''):
        line = line.decode("utf-8")
        if line == '' :
            break
        else:
            #dict = dict(element.split(":") for element in line.decode("utf-8").split(";") if element)
            return ast.literal_eval(line)
