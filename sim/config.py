CONFIG_VARS= ['numprocess', 'meandev', 'standdev', 'iotime', 'runtime', 'bursts']

class SimConfig:
    def __init__(self, vardict):
        for k,v in vardict.items():
            setattr(self, k, v)


def configFromFile(filename):
    values= {}
    bursts=[]
    lines= open(filename).readlines()
    for line in lines:
        try:
            k,v= line.split(" ")
            if k in CONFIG_VARS:
                values[k]= int(v)
            elif k=="burst":
                    bursts.append( int(v) )
            elif k[:2]=="//":
                #line is a comment
                pass
            else:
                raise Exception("Not recognized k,v: "+k+","+v)
        except:
            pass

    assert len(bursts)==values['numprocess']                #data for all processes present
    values['bursts']= bursts
    assert sorted(values.keys()) == sorted(CONFIG_VARS)     #all variables present
    return SimConfig(values)
