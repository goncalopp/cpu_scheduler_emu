from hardware.ram import PROGRAM_MEMORY_START
import logging
log= logging.getLogger('os')

class NotEnoughRamInBlock( Exception ):
    pass

class NotEnoughRamInBlockList( Exception ):
    pass

class FreeUnallocatedMemory( Exception ):
    pass

class OutOfRam( Exception ):
    pass

class RamBlock:
    '''represents a ram block (a start and end address'''
    def __init__(self, start_address, end_address):
        assert start_address<=end_address
        self.start, self.end= start_address, end_address

    def __len__(self):
        return self.end-self.start+1

    def partition(self, offset):
        '''partitions this block into two'''
        if len(self)<=offset:
            raise NotEnoughRamInBlock()
        else:
            b1= RamBlock(self.start, self.start+offset-1)
            b2= RamBlock(self.start+offset, self.end)
            return (b1,b2)
    def __repr__(self):
        return "<RamBlock: "+str(self.start)+" - "+str(self.end)+" >"

class RamBlockList:
    '''represents a collection of ram blocks, with functions for removing and inserting blocks'''
    def __init__(self, start_address, end_address):
        self.blocks= [ RamBlock(start_address, end_address) ]

    def remove( self, n_blocks ):
        for i,block in enumerate(self.blocks):
            if len(block)>n_blocks: #this block has enough
                requested, remaining= block.partition(n_blocks)
                self.blocks.pop(i)  #old block is now invalid...
                self.blocks.append(remaining)
                return requested
        raise NotEnoughRamInBlockList()

    def insert( self, block ):
        assert isinstance(block, RamBlock)
        following= filter(lambda x: x.start==block.end+1, self.blocks)
        previous= filter(lambda x: x.end==block.start-1, self.blocks)
        if len(following)==1 and len(previous)==1:
            #block 'bridges' two existing ones
            self.blocks.remove(following[0])   #remove the second one
            previous[0].end= following[0].end     #fill in the returned block
        elif len(following)==1:    #block is immediatelly before "following"
            following[0].start= block.start    #add returned block to pool
        elif len(previous)==1:    #block is immediatelly after to "previous"
            previous[0].end= block.end    #add returned block to pool
        else:
            self.blocks.append(block)   #block is not contiguous to current blocks

    def __repr__(self):
        return "<RamBlockList\n\t"+"\n\t".join(map(str,self.blocks))+"\n>"


class MemoryAllocator:
    '''Ineficient but correct'''
    def __init__(self, os):
        log.debug("initializing memory allocator")
        self.os= os
        self.bl= RamBlockList( PROGRAM_MEMORY_START, len(self.os.machine.ram))
        self.allocated_blocks=[]

    def allocate( self, n_cells):
        '''returns start of allocated block'''
        try:
            allocated= self.bl.remove( n_cells)
            self.allocated_blocks.append( allocated )
        except NotEnoughRamInBlockList:
            raise OutOfRam()
        return allocated.start

    def free( self, block_start ):
        allocateds= filter(lambda x: x.start== block_start, self.allocated_blocks)
        if len(allocateds)!=1:
            raise FreeUnallocatedMemory()
        self.bl.insert( allocateds[0] )
        self.allocated_blocks.remove(allocateds[0])

    def set_callback( self, f ):
        assert callable(f)
        self.callback= f

    def timer_interrupt_handler(self):
        log.debug("handling interrupt")
        self.callback()

