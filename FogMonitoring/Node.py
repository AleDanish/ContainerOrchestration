import uuid
import Config

class Node:
    '''
    general Node class
    '''
    
    def __init__(self, nid=uuid.uuid4(), monitoringFunction=Config.monitoringFunction, weight=1):
        '''
        Constructor
        args:
            @param env: enviroment creating Node, called for communication, msg passing
            @param nid: unique node id
            @param weight: node's weight
        '''
        
        self.vLast=0
        self.u=0
        self.delta=0
        self.e=0
        self.coeff=0
        
        self.id=nid
        self.weight=weight
        self.threshold=0
        self.monitoringFunction=monitoringFunction
    
    '''
    --------------getters
    '''
    def getWeight(self):
        return self.weight
    
    def getId(self):
        return self.id
    
    '''
    -------------node execution
    '''
    #def check(self):
    #    '''
    #    performs threshold check of drift vector's function value: f(u)
    #    '''
        
        #DBG
    #    print('--Node %s reporting u: %f'%(self.id,self.u))
        
    #    if self.monitoringFunction(self.u)>=self.threshold:
    #        self.rep()
        
    def run(self, vector):
        '''
        main Monitoring Node function
        receive, process updates
        '''
        self.v=vector
    #    self.u=self.e+(self.v-self.vLast)+(self.delta/self.weight)
        self.u=[(e_i+v_i-vLast_i)+(self.delta/self.weight) for e_i,v_i,vLast_i in zip(self.e,self.v,self.vLast)]
        self.vLast=self.v
    
    '''
    ------------signal handling
    '''
    def send(self,target,msg,data):
        '''
            calls enviroment method "signal"
            tuple (id, target id, message, data)
        '''
        if not isinstance(target, list):
            target=[target]
        if not isinstance(data, list):
            data=[data]
        for targ,dat in zip(target,len(target)==len(data) and data or data*len(target)): #to cover cases of multiple targets, one data | multiple targets, multiple data
            self.env.signal((self.id,targ , msg, dat))
        
    def rcv(self,data):
        '''
            is called by env
            data is tuple (sender id, target id , msg, data)
        '''
        if data[1]==self.id:
            if data:
                getattr(self, data[2])(data[3],data[0])
