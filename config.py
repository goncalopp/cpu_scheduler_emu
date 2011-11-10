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
        try:
            k,v= line.split(" ")
            if k in CONFIG_VARS:
                values[k]= int(v)
            elif k=="burst":
                process_bursts.append( int(v) )
            elif k=="iodevice":
                process_ios.append( int(v))
            elif k=="iotime":
                iotimes.append( int(v))
            elif k[:2]=="//":
                #line is a comment
                pass
            else:
                raise Exception("Not recognized k,v: "+k+","+v)
        except:
            pass
    if not "iodevices" in values:
        values["iodevices"]=1  #default
    if len(process_ios)==0:
        process_ios=[0]*values['numprocess']
    assert len(process_bursts)==values['numprocess']                #data for all processes present
    assert len(process_ios)==values['numprocess']                #data for all processes present
    
    values['process_bursts']= process_bursts
    values['process_ios']= process_ios
    values['iotimes']= iotimes
    
    assert sorted(values.keys()) == sorted(CONFIG_VARS)     #all variables present
    return SimConfig(values)
