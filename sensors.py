import logging
import random

def returnbounds(val, min, max):
    if val < min:
        return min
    if val > max:
        return max
    return val

def inttointlist(val, bytesize):
    b_array = int(val).to_bytes(bytesize, byteorder='big')
    return [int(x) for x in b_array] 

class RandHistory(object):
    def __init__(self, initval=0, bytesize=1, randstep=1):
        self.min=0
        self.max=2**(bytesize*8)
        self.bytesize=bytesize
        self.randstep=randstep
        self.value=initval

    def next(self):
        step = random.randint(-self.randstep, self.randstep)
        self.value+=step

        self.value = returnbounds(self.value, self.min, self.max)

        return inttointlist(self.value, self.bytesize)

    def get_bytesize(self):
        return  self.bytesize


class SupportedPids(object):
    def __init__(self, sensordict):
        supportedarray = []
        
        for x in range(1,20):
            if x in sensordict:
                supportedarray.append(1)
            else:
                supportedarray.append(0)

        self.supportedarray = supportedarray


    def get_supportedarray(self):
        return self.supportedarray

    def get_bytesize(self):
        return 4

    def next(self):
        returnlist = [sum(b*2**x for b,x in zip(byte[::-1],range(8))) for byte in zip(*([iter(self.supportedarray)]*8))] + [0,0,0,0]

        return returnlist[0:4]
