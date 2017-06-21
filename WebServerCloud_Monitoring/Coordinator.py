import random
import Config
from Node import Node
from Utils import dec,deDec

class Coordinator(Node):
    ''' geometric monitoring, Coordinator node '''


    def __init__(self, nodes, 
                 nid="Coord", 
                 threshold=Config.threshold, 
                 monitoringFunction=None):
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
        self.balancingSet=set() #set containing tuples (nodeId,v,u) if classicBalance, (nodeId,v,u,vel) if heuristicBalance
        self.sumW=sum(nodes.values())
        
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
            w=dec(dat[1])
            v=dec(dat[0])
            self.e+=(w*v)/self.sumW
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
        self.balancingSet.add((sender,)+dat)
        
        b=sum(u*self.nodes[i] for i,v,u in self.balancingSet)/sum(self.nodes[i] for i,v,u in self.balancingSet)
        
        #DBG
        if len(self.balancingSet)==1:
            print("Coord:LOCAL VIOLATION")
        else:
            print("balancing set is:")
            print(self.balancingSet)
            
        print("Coord: balance vector is: %f,f(b)= %f, threshold is %f"%(b,self.monitoringFunction(b),self.threshold))
        
        if self.monitoringFunction(b)<self.threshold:
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
                vGl=sum(v*self.nodes[i] for i,v,u in self.balancingSet)/sum(self.nodes[i] for i,v,u in self.balancingSet)   #global stats vector
                uGl=sum(u*self.nodes[i] for i,v,u in self.balancingSet)/sum(self.nodes[i] for i,v,u in self.balancingSet)   #global stats vector (via drift vectors *convexity property*)
                
                #EXP - log balancing vector
                #self.send(None, "balancingVector", b)
                
                #DBG
                print("Coord: GLOBAL VIOLATION:v=%f,u=%f,f(v)=%f"%(vGl,uGl,self.monitoringFunction(vGl)))
                
                self.e=vGl
                
                self.balancingSet.clear()
                
                #self.newEst()
                
                #self.globalViolation()
                return self.e, "global_violation"
                      
#----------------------------------------------------------------------------
#---------------------------------TEST---------------------------------------
#----------------------------------------------------------------------------
         
#see Enviroment module