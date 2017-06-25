import subprocess
import ast
import Config
import socket

def send(mode, filename=None, mac=None):
    hostname = socket.gethostname()
    cmd="curl http://" + Config.WEB_SERVER_IP + ":" + Config.WEB_SERVER_PORT + " -F mode=" + mode + " -F hostname=" + hostname
    if filename is not None:
        cmd+=" -F file=@"+filename
    elif mac is not None:
        cmd+=" -F mac="+mac
    proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
    for line in iter(proc.stdout.readline,''):
        line = line.decode("utf-8")
        if line == '' :
            break
        else:
            #dict = dict(element.split(":") for element in line.decode("utf-8").split(";") if element)
            return ast.literal_eval(line)

def send_noresp(mode, v, u):
    hostname = socket.gethostname()
    cmd="curl http://" + Config.WEB_SERVER_IP + ":" + Config.WEB_SERVER_PORT + " -F mode=" + mode + " -F hostname=" + hostname
    cmd += " -F v0=" + str(v[0]) + " -F v1=" + str(v[1]) + " -F v2=" + str(v[2]) + " -F u0=" + str(u[0]) + " -F u1=" + str(u[1]) + " -F u2=" + str(u[2]) 
    subprocess.Popen(cmd, shell=True)