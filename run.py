CONFIG_DIR= "configs"

import sys, os
sys.path.append("operating_system")
import boot
import config


def cli_choice(question, answers, return_index=False):
    n= len(answers)
    print question
    for i,answer in enumerate(answers):
        print str(i+1)+")\t"+answer
    while True:
        print ">",
        try:
            index= int(raw_input())-1
            if return_index:
                return index
            else: 
                return answers[index]
        except (ValueError, IndexError):
            print "Invalid choice"

def run_sim_from_config( cfg_file ):
    print "parsing config file"
    cfg= config.configFromFile( os.path.join( CONFIG_DIR, cfg_file ))
    boot.simulate( config=cfg )

def run_correctness_tests():
    print "running correctness tests"
    from hardware import verification_programs
    tests= verification_programs.tests
    programs= [t.program for t in tests]
    pc, os= boot.simulate( programs=programs )
    for test in tests:
        test.verify( pc.ram, test.program.process_start_address )
        print "test",test.name,"passed!"    #since if it doesn't, a exception is raised

if cli_choice("What to do?", ("Run simulation from a config file","Run correctness checks"), return_index=True)==0:
    config_files= os.listdir( CONFIG_DIR)
    cfg_file= cli_choice( "Please choose the config file to use:",config_files )
    run_sim_from_config( cfg_file )
else:
    run_correctness_tests()
