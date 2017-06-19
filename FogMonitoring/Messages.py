import subprocess
from Utils import dec, deDec

WEB_SERVER_PORT="8889"
WEB_SERVER_IP="192.168.56.101"

def send(hostname, mode, v=None, u=None):
    if (v is None) and (u is None):
        cmd="curl -d hostname="+hostname+" -d mode="+mode+" http://"+WEB_SERVER_IP+":"+WEB_SERVER_PORT
    else:
        cmd="curl -d hostname="+hostname+" -d mode="+mode+" -d v="+str(v)+" -d u="+str(u)+" http://"+WEB_SERVER_IP+":"+WEB_SERVER_PORT
    proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
    dictionary = {}
    for line in iter(proc.stdout.readline,''):
        line = line.decode("utf-8")
        if line == '' :
            break
        else:
            #dict = dict(element.split(":") for element in line.decode("utf-8").split(";") if element)
            line = line.split(":")
            dictionary = {line[0].replace("\"","").split("{")[1]:dec(line[1].replace("\"","").split("}")[0].strip())}
    return dictionary 