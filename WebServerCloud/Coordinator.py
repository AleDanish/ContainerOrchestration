import Config
import numpy as np

class Coordinator():
    ''' geometric monitoring, Coordinator node '''

    def __init__(self, 
                 threshold=Config.THRESHOLD_DEFAULT, 
                 monitoringFunction=Config.MONITORING_FUNCTION):
        self.weight=0
        self.threshold=threshold
        self.monitoringFunction=monitoringFunction
        self.balancingSet=[] #set containing tuples (nodeId,v,u) if classicBalance, (nodeId,v,u,vel) if heuristicBalance
        self.coeff=0
        self.e=0
    def init_estimation(self,dat,sumW):
        V=dat[0]
        w=dat[1]
        self.e=(w*V)/sumW
        return self.e
    def setMonitoringFunction(self, function):
        self.monitoringFunction=function
    def balance(self):
        sumU=[0,0,0]
        sumW=0
        for i,V,U in self.balancingSet:
            for index in range(0,3):
                sumU[index]+=U[index]*self.nodes[i]
            sumW+=self.nodes[i]
            disk = U[2]
        b = np.array(sumU)/sumW
        b[2] = disk
        print("balancing set is:" + str(self.balancingSet))

        valueMonitoring = self.monitoringFunction(self.coeff, b)
        print("Coord: balance vector is: " + "".join(str(x)+" " for x in b) + ", f(b)= %f, threshold is %f"%(valueMonitoring,self.threshold))
        
        if valueMonitoring < self.threshold:
            #SUCESSfull balancing
            dDelta=[]
            for (i,v,u) in self.balancingSet:
                dDelta.append([i, self.nodes[i]*b-self.nodes[i]*u])
            
            self.balancingSet.clear()
            print("Balance successful")
            print("dDelta:" + str(dDelta))
            return dDelta, "balanced"
        else:
            #Failed balancing
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
                values=[]
                for (i,v,u) in self.balancingSet:
                    values.append([i, self.e])
                
                self.balancingSet.clear()
                return values, "violation"
    def balance_down(self):
        sumU=[0,0,0]
        sumW=0
        for i,V,U in self.balancingSet:
            for index in range(0,3):
                sumU[index]+=U[index]*self.nodes[i]
            sumW+=self.nodes[i]
            disk = U[2]
        b = np.array(sumU)/sumW
        b[2] = disk
        print("balancing set is:" + str(self.balancingSet))

        valueMonitoring = self.monitoringFunction(self.coeff, b)
        print("Coord: balance vector is: " + "".join(str(x)+" " for x in b) + ", f(b)= %f, threshold is %f"%(valueMonitoring,self.threshold))
        
        if valueMonitoring < self.threshold:
            #SUCESSfull balancing
            dDelta=[]
            for (i,v,u) in self.balancingSet:
                dDelta.append([i, self.nodes[i]*b-self.nodes[i]*u])
            
            self.balancingSet.clear()
            print("Balance successful")
            print("dDelta:" + str(dDelta))
            return dDelta, "balanced"
        else:
            #Failed balancing
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
                values=[]
                for (i,v,u) in self.balancingSet:
                    values.append([i, self.e])
                
                self.balancingSet.clear()
                return values, "global_violation"
            