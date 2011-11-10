import sys
CONFIG_VARS= ['iodevices', 'iotimes', 'numprocess', 'meandev', 'standdev', 'runtime', 'process_bursts', 'process_ios']

class SimConfig:
    def __init__(self, vardict):
        for k,v in vardict.items():
            setattr(self, k, v)


def configFromFile(filename):
    values= {}
    process_bursts=[]
    process_ios=[]
    iotimes=[]
    lines= open(filename).readlines()
    for line in lines:
        if not line.startswith("//"):
            try:
                k,v= line.split(" ")
                if k=="burst":
                    process_bursts.append( int(v) )
                elif k=="iodevice":
                    process_ios.append( int(v))
                elif k=="iotime":
                    iotimes.append( int(v))
                elif k=="processgenerate":
                    try:
                        a1,a2= v.split(",")
                        a1,a2=int(a1), float(a2)
                        values["processgenerate_interval"],values["processgenerate_prob"]= a1,a2
                    except:
                        raise Exception ("wrong processgenerate syntax (space after comma?)")
                elif k in CONFIG_VARS:
                    values[k]= int(v)
                else:
                    raise Exception("Not recognized k,v: "+k+","+v)
            except:
                print "BAD CONFIG LINE:", line, sys.exc_info()[1]
    if not "iodevices" in values:
        values["iodevices"]=1  #default
    if len(process_ios)==0:
        process_ios=[0]*values['numprocess']
    assert len(process_bursts)==values['numprocess']                #data for all processes present
    assert len(process_ios)==values['numprocess']                #data for all processes present
    
    values['process_bursts']= process_bursts
    values['process_ios']= process_ios
    values['iotimes']= iotimes
    
    assert all( [c in values.keys() for c in CONFIG_VARS])     #all variables present
    return SimConfig(values)
