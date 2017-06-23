import random
import Config
from Node import Node
from Utils import dec,deDec
import numpy as np

class Coordinator(Node):
    ''' geometric monitoring, Coordinator node '''


    def __init__(self, nodes, 
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
        
        Node.__init__(self,  nid=nid, weight=0)
        
        self.threshold=threshold
        self.monitoringFunction=monitoringFunction
        
        self.nodes=nodes    #dictionary {"id":weight,}
        self.balancingSet=[] #set containing tuples (nodeId,v,u) if classicBalance, (nodeId,v,u,vel) if heuristicBalance
        self.sumW=sum(nodes.values())
        self.coeff=0
        
        self.e=0
        
    '''
    ----------------------------------------------------------------------
    messages methods:
    incoming: methodName(self,data,sender) format
    ----------------------------------------------------------------------

    '''
    def init(self,dat,sender):
        '''
            "init" signal
            "init" msg sent by all nodes for monitoring initialization
        '''
        if sender:
            #self.balancingSet.add(sender)
            V=dat[0]
            w=dat[1]
            self.e+=(w*V)/self.sumW
            if len(self.balancingSet)==len(self.nodes):
                self.balancingSet.clear()
                #self.newEst()
        return self.e
    
    def setMonitoringFunction(self, function):
        self.monitoringFunction=function
    
    def setNodes(self, nodes):
        self.nodes=nodes
        self.sumW=sum(nodes.values())
    
    #def rep(self,dat,sender):
        '''
            @override
            "rep" signal for classic balancing
            at each "rep" msg initiate balancing process
        '''
    #    self.balancingSet.add((sender,)+dat)    
    #    self.balance()
    
    '''
    ----------------------------------------------------------------------
    messages methods:
    outgoing: methodName(self) format
    ----------------------------------------------------------------------
    '''
    #def newEst(self):
        #'''
        #    "newEst" signal
        #    "newEst" mgs sent to nodes at monitoring initialization/global Violation occurence
        #'''
    #    self.send(self.nodes.keys(),"newEst",self.e)
        
    #def req(self,nodeId):
        #'''
        #    "req" signal
        #    "req" msg sent to nodeId to request data for balancing
        #'''
        #self.send(nodeId,"req",None)
        
    #def adjSlk(self,nodeId,dat):
        #'''
        #    "adjSlk" signal
        #    "adjSlk" msg sent at balance success
        #'''
    #    self.send(nodeId,"adjSlk",dat)
        
    #def globalViolation(self):
        #'''
        #    "globalViolation" signal
        #    "globalViolation" msg (not in original Geometric Monitoring method) sent at global violation occurence
        #'''
    #    self.send(self.nodes.keys(),"globalViolation",None)
        
        
        
    '''
    ----------------------------------------------------------------------------------------------------------------
    ********************************************BALANCING FUNCTIONS*************************************************
    ----------------------------------------------------------------------------------------------------------------

    '''
    def balance(self, dat, sender):
        '''
            @override
            balance method based on original paper
        '''
        self.balancingSet.append([sender,dat[0], dat[1]])
        
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
        
        if abs(valueMonitoring) < self.threshold:
            #----------------------------------------------------------------
            #SUCESSfull balancing
            #----------------------------------------------------------------
            dDelta=[]
            nodeIds=[]
            for (i,v,u) in self.balancingSet:
                dDelta.append(self.nodes[i]*b-self.nodes[i]*u)
                nodeIds.append(i)
            
            #DBG
            print("Coord: balance success")
            print("dDelta:")
            print(dDelta)
            
            #EXP - log balancing vector
            #self.send(None, "balancingVector", b)
            
            self.balancingSet.clear()

            #self.adjSlk(nodeIds, dDelta)
                    
        else:
            #-----------------------------------------------------------------
            #FAILed balancing or only 1 node
            #-----------------------------------------------------------------
            diffSet=set(self.nodes.keys())-set(i for i,v,u in self.balancingSet) #check if other nodes (that belong to the same cluster) are available 
            
            if len(diffSet): #i.e. len(balancingSet)!=len(nodes)
                reqNodeId=random.sample(diffSet,1)[0]   #request new node data at random
                self.balance(reqNodeId)
            
            else:
                
                #----------------
                # 1 Node - Global Violation
                #----------------
                
                sumV=[0,0,0]
                sumU=[0,0,0]
                for i,V,U in self.balancingSet:
                    for index in range(0,3):
                        sumV[index]+=V[index]*self.nodes[i]
                        sumU[index]+=U[index]*self.nodes[i]
                vGl = np.array(sumV)/sum(self.nodes[i] for i,v,u in self.balancingSet)
                uGl = np.array(sumU)/sum(self.nodes[i] for i,v,u in self.balancingSet)
                
                #vGl=sum(v*self.nodes[i] for i,v,u in self.balancingSet)/sum(self.nodes[i] for i,v,u in self.balancingSet)   #global stats vector
                #uGl=sum(u*self.nodes[i] for i,v,u in self.balancingSet)/sum(self.nodes[i] for i,v,u in self.balancingSet)   #global stats vector (via drift vectors *convexity property*)
                
                #EXP - log balancing vector
                #self.send(None, "balancingVector", b)
                
                #DBG
                print("Coord: GLOBAL VIOLATION:v="  + "".join(str(vGl)) + ",u=" + "".join(str(uGl)) + " ,f(v)=%f"%(self.monitoringFunction(self.coeff, vGl)))
                
                self.e=vGl
                
                self.balancingSet.clear()
                
                #self.newEst()
                
                #self.globalViolation()
                return self.e, "global_violation"
                      
#----------------------------------------------------------------------------
#---------------------------------TEST---------------------------------------
#----------------------------------------------------------------------------
         
#see Enviroment module