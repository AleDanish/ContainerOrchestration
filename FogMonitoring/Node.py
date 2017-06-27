import uuid
import Config

class Node:
    def __init__(self, nid=uuid.uuid4(), monitoringFunction=Config.monitoringFunction, weight=1):
        self.vLast=0
        self.u=0
        self.delta=[0,0,0]
        self.e=0
        self.coeff=0
        
        self.id=nid
        self.weight=weight
        self.threshold=0
        self.monitoringFunction=monitoringFunction
    
    def getWeight(self):
        return self.weight
    
    def getId(self):
        return self.id
        
    def run(self, vector):
        self.v=vector
        self.u=[(e_i+v_i-vLast_i)+(d_i/self.weight) for e_i,v_i,vLast_i,d_i in zip(self.e,self.v,self.vLast,self.delta)]
        self.vLast=self.v
    
    #def send(self,target,msg,data):
    #    if not isinstance(target, list):
    #        target=[target]
    #    if not isinstance(data, list):
    #        data=[data]
    #    for targ,dat in zip(target,len(target)==len(data) and data or data*len(target)): #to cover cases of multiple targets, one data | multiple targets, multiple data
    #        self.env.signal((self.id,targ , msg, dat))
        
    # def rcv(self,data):
    #    if data[1]==self.id:
    #        if data:
    #            getattr(self, data[2])(data[3],data[0])
