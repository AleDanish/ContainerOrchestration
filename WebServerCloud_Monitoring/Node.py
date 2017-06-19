'''
@author: ak
'''
import uuid

from Utils import dec, deDec


class Node:
    '''
    general Node class
    '''
    
    def __init__(self,nid=uuid.uuid4(), weight=1):
        '''
        Constructor
        args:
            @param env: enviroment creating Node, called for communication, msg passing
            @param nid: unique node id
            @param weight: node's weight
        '''
        #self.env=env
        self.id=nid
        self.weight=weight
        
        #convert to decimals
        self.weight=dec(self.weight)
    
    '''
    --------------getters
    '''
    def getWeight(self):
        return self.weight
    
    def getId(self):
        return self.id
    
