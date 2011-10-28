from cpu_instruction import programFromString, Program
from ram import RAM
import random

#def model_verification_function(program_ram_slice):
#    if not program_ram_slice is great:
#        raise VerificationFailed()

    
class VerificationFailed( Exception ):
    pass

class VerificationProgram:
    '''a program with a function to check finishing state for correction of execution'''
    def __init__(self, name, program, verification_function):
        self.name= name
        self.program= program
        self.verification_function= verification_function
        
    def verify(self, ram, program_location):
        assert isinstance(ram, RAM)
        i1= program_location
        i2= i1+len(self.program)
        ram_slice= ram[i1:i2]
        self.verification_function( ram_slice )
            



#-----------------------------------------------------------------------

FIB_ITERATIONS= random.randint(5,35)
fib_code= '''
-{ITER}                 //0: number of iterations (negative)
0                       //1: current iteration
0                       //2: temporary storage for variable swap
0                       //3: (i-2)th fibonacci number
1                       //4: (i-1)th   fibonacci number
LOAD_REL    $1          //load iteration counter
ADD         1           //increment it
STOR        $1          //and save it
ADD_REL	    $0          //compare current iteration with finish iteration
JZ          $17         //if we're finished, jump to end
LOAD_REL    $4          //load i-1 fib
STOR        $2          //store to temporary storage
ADD_REL     $3          //calculate fib i
STOR        $4          //store i on position of i-1
LOAD_REL    $2          //load i-1 from temporary storage
STOR        $3          //store i-1 in position of i-2
JMP         $5          //loop end
NOOP                    //17: program end
'''.format(ITER=FIB_ITERATIONS)

def fib_ver( r ):
    reality= [0, 1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144, 233, 377, 610, 987, 1597, 2584, 4181, 6765, 10946, 17711, 28657, 46368, 75025, 121393, 196418, 317811, 514229, 832040, 1346269, 2178309, 3524578, 5702887, 9227465, 14930352, 24157817]
    assert 2<=FIB_ITERATIONS<len(reality)
    got= r[4]
    expected= reality[FIB_ITERATIONS] 
    if got!=expected:
        raise VerificationFailed("Expected {a}, got {b}".format(a=expected, b=got))

fib= VerificationProgram("fibonacci ({n} iterations)".format(n=FIB_ITERATIONS), programFromString(fib_code, 5), fib_ver)

#-----------------------------------------------------------------------

tests= [fib]
