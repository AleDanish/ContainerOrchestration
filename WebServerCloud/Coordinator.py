import Config
import numpy as np

class Coordinator():
    ''' geometric monitoring, Coordinator node '''

    def __init__(self, 
                 nid="Coord", 
                 threshold=Config.THRESHOLD_DEFAULT, 
                 monitoringFunction=Config.MONITORING_FUNCTION):
        '''
        Constructor
        args:
             ------node params
            @param nid: unique node id - "Coord"
            ------geometric monitoring params
            @param env: networking/monitoring enviroment creating Coordinator
            @param threshold: monitoring threshold
            @param monitoringFunction: monitoring function
        '''
        
        self.nid=nid
        self.weight=0
        
        self.threshold=threshold
        self.monitoringFunction=monitoringFunction
        
        #self.nodes=[]    #dictionary {"id":weight,}
        self.balancingSet=[] #set containing tuples (nodeId,v,u) if classicBalance, (nodeId,v,u,vel) if heuristicBalance
        # self.sumW=0
        self.coeff=0
        
        self.e=0
        
    '''
    ----------------------------------------------------------------------
    messages methods:
    incoming: methodName(self,data,sender) format
    ----------------------------------------------------------------------

    '''
    def init_estimation(self,dat,sender, sumW):
        '''
            "init" signal
            "init" msg sent by all nodes for monitoring initialization
        '''
        #if sender:
            #self.balancingSet.add(sender)
            #V=dat[0]
            #w=dat[1]
            #self.e=(w*V)/sumW
            #if len(self.balancingSet)==len(self.nodes):
            #    self.balancingSet.clear()
                #self.newEst()
        V=dat[0]
        w=dat[1]
        self.e=(w*V)/sumW
        return self.e
    
    def setMonitoringFunction(self, function):
        self.monitoringFunction=function
    
    #def setNodes(self, nodes):
    #    self.nodes=nodes
    #    self.sumW=sum(nodes.values())
    
    '''
    ----------------------------------------------------------------------------------------------------------------
    ********************************************BALANCING FUNCTIONS*************************************************
    ----------------------------------------------------------------------------------------------------------------

    '''
    #def estimation(self, dat, sender):
        
    #    self.balancingSet.append([sender,dat[0], dat[1]])    
    #    self.balance()
        
    def balance(self):
        '''
            @override
            balance method based on original paper
        '''
        
        sumU=[0,0,0]
        sumW=0
        for i,V,U in self.balancingSet:
            for index in range(0,3):
                sumU[index]+=U[index]*self.nodes[i]
            sumW+=self.nodes[i]
        b = np.array(sumU)/sumW

        #DBG
        if len(self.balancingSet)==1:
            print("Coord:LOCAL VIOLATION")
        else:
            print("balancing set is:")
            print(self.balancingSet)

        valueMonitoring = self.monitoringFunction(self.coeff, b)            
        print("Coord: balance vector is: " + "".join(str(x)+" " for x in b) + ", f(b)= %f, threshold is %f"%(valueMonitoring,self.threshold))
        
        if valueMonitoring < self.threshold:
            #----------------------------------------------------------------
            #SUCESSfull balancing
            #----------------------------------------------------------------
            dDelta=[]
            #nodeIds=[]
            for (i,v,u) in self.balancingSet:
                dDelta.append([i, self.nodes[i]*b-self.nodes[i]*u])
                #nodeIds.append(i)
            
            self.balancingSet.clear()
            print("Balance successfull")
            print("dDelta:" + str(dDelta))
            return dDelta, "balanced"
        else:
            #-----------------------------------------------------------------
            #FAILed balancing or only 1 node
            #-----------------------------------------------------------------
            #diffSet=set(self.nodes.keys())-set(i for i,v,u in self.balancingSet) #check if other nodes (that belong to the same cluster) are available 
            
            #if len(diffSet): #i.e. len(balancingSet)!=len(nodes)
            #    reqNodeId=random.sample(diffSet,1)[0]   #request new node data at random
                #Deploy new node
            
            #else:
                # 1 Node - Global Violation
                sumV=[0,0,0]
                sumU=[0,0,0]
                for i,V,U in self.balancingSet:
                    for index in range(0,3):
                        sumV[index]+=V[index]*self.nodes[i]
                        sumU[index]+=U[index]*self.nodes[i]
                vGl = np.array(sumV)/sum(self.nodes[i] for i,v,u in self.balancingSet)
                uGl = np.array(sumU)/sum(self.nodes[i] for i,v,u in self.balancingSet)
                print("Coord: GLOBAL VIOLATION:v="  + str(vGl) + ",u=" + str(uGl) + " ,f(v)=%f"%(self.monitoringFunction(self.coeff, vGl)))
                
                self.e=vGl
                
                self.balancingSet.clear()
                return self.e, "global_violation"
            