import uuid

from Utils import dec, deDec

class Node:
    
    def __init__(self,nid=uuid.uuid4(), weight=1):
        self.id=nid
        self.weight=weight
        self.weight=dec(self.weight)

    def getWeight(self):
        return self.weight
    
    def getId(self):
        return self.id