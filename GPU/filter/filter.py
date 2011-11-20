#!/usr/bin/python

class PrefixSum:
    import numpy as np
    HOST_TYPE_DATA = np.float32
    HOST_TYPE_KEYS = np.uint8
    
    GPU_TYPE_DATA = 'float'
    GPU_TYPE_KEYS = 'uchar'

    
    FILE_NAME = 'kernels.cl'
    
    RETURN_FILTER = 0
    
    def get_grid_dims(self, ndata):
        import numpy as np
        return (int(np.ceil(1.0*ndata/self.localSize)), 1, 1)
    
    def get_global(self, grid):
        return (grid[0]*self.localDims[0], grid[1]*self.localDims[1], grid[2]*self.localDims[2])
    
    def __init__(self, fileName, localDims, listFile = False ):
        import pyopencl as cl
        import numpy as np
        import io
        
        self.localDims = localDims
        self.localSize = np.prod(localDims)
        
        mf = cl.mem_flags
        
        self.ctx = cl.create_some_context(interactive=False, answers=0)
        #self.ctx = cl.Context(devices=cl.get_platforms()[1].get_devices())
        self.queue = cl.CommandQueue(self.ctx, properties = cl.command_queue_properties.PROFILING_ENABLE)
        
        f = io.open(fileName)
        try: lines = f.readlines()
        finally: f.close()
        
        src = [ '%s\n' % s for s in (
                        '#define DATA_T %s' % PrefixSum.GPU_TYPE_DATA,
                        '#define KEYS_T %s' % PrefixSum.GPU_TYPE_KEYS,
                        '#define LSIZE %d' % self.localSize,
                        '#define RETURN_FILTER %d' % PrefixSum.RETURN_FILTER) ]
        src += lines
        src = ''.join(src)
        
        print src
        self.prg = cl.Program(self.ctx, src).build()

    def filterPrepare(self, e, data, keys, ndata, events):
        import numpy as np
        import pyopencl as cl
        mf = cl.mem_flags
        
        ndata = data.size
        if keys.size != ndata: raise Exception()
        
        filtbytes = np.bool8(False).nbytes * ndata
        
        if not isinstance(data, cl.Buffer):
            data_buf = cl.Buffer(self.ctx, mf.READ_ONLY | mf.COPY_HOST_PTR, hostbuf= data)
        else:
            data_buf = data
        
        if not isinstance(keys, cl.Buffer):
            keys_buf = cl.Buffer(self.ctx, mf.READ_ONLY | mf.COPY_HOST_PTR, hostbuf= keys)
        else:
            keys_buf = keys
        
        filt_buf = cl.Buffer(self.ctx, mf.READ_WRITE, filtbytes)
        
        kernel = self.prg.filterPrepare
        kernel.set_args(data_buf, keys_buf, np.uint64(ndata), np.uint8(33), np.uint8(66), filt_buf)
        global_dims = self.get_global(self.get_grid_dims(ndata))
        
        if e is None:
            e  = [ cl.enqueue_nd_range_kernel(self.queue, kernel, global_dims, self.localDims), ]
        else:
            e  = [ cl.enqueue_nd_range_kernel(self.queue, kernel, global_dims, self.localDims, wait_for=e), ]
        events += e
        
        return (e, data_buf, keys_buf, filt_buf)

    def prefixSum(self, e, data, keys, ndata, low, hi, events):
        import numpy as np
        import pyopencl as cl
        mf = cl.mem_flags
        
        if not isinstance(data, cl.Buffer):
            data_buf = cl.Buffer(self.ctx, mf.READ_ONLY | mf.COPY_HOST_PTR, hostbuf= data)
        else:
            data_buf = data
        
        if not isinstance(keys, cl.Buffer):
            keys_buf = cl.Buffer(self.ctx, mf.READ_ONLY | mf.COPY_HOST_PTR, hostbuf= keys)
        else:
            keys_buf = keys
        
        psumbytes = ndata * np.uint64(0).nbytes
        bsumbytes = int(np.ceil(1.0*ndata/self.localSize)) * np.uint64(0).nbytes
        nbsumbytes =  np.uint64(0).nbytes
        
        psum_buf = cl.Buffer(self.ctx, mf.READ_WRITE, psumbytes)
        bsum_buf = cl.Buffer(self.ctx, mf.READ_WRITE, bsumbytes)
        nbsum_buf = cl.Buffer(self.ctx, mf.READ_WRITE, nbsumbytes)
        
        low = PrefixSum.HOST_TYPE_KEYS(low)
        hi = PrefixSum.HOST_TYPE_KEYS(hi)
        
        kernel = self.prg.prefixSumDown
        kernel.set_args(data_buf, keys_buf, np.uint64(ndata), low, hi, psum_buf, bsum_buf, nbsum_buf)
        
        global_dims = self.get_global(self.get_grid_dims(ndata))
        
        if e is None:
            e  = ( cl.enqueue_nd_range_kernel(self.queue, kernel, global_dims, self.localDims, wait_for=e), )
        else:
            e  = ( cl.enqueue_nd_range_kernel(self.queue, kernel, global_dims, self.localDims), )
        events += e
        
        nbsum = np.zeros(1, dtype = np.uint64)
        events += (cl.enqueue_copy(self.queue, nbsum, nbsum_buf, wait_for=e),)
        
        if nbsum>1:
            (e, bsum_buf, bsum1_buf, nbsum1_buf, ndata2) = self.prefixSumDownInplace(e, bsum_buf, nbsum.item(), events)
        else:
            ndata2 = np.zeros(1, dtype = np.uint64)
            events += (cl.enqueue_copy(self.queue, ndata2, bsum_buf, wait_for=e),)
            ndata2 = ndata2.item()
        
        self.prefixSumUp(e, psum_buf, ndata, bsum_buf, nbsum, events)
        
        return (e, data_buf, keys_buf, psum_buf, bsum_buf, nbsum_buf, ndata2)
    
    def prefixSumDownInplace(self, e, data, ndata, events):
        import numpy as np
        import pyopencl as cl
        mf = cl.mem_flags
        
        if not isinstance(data, cl.Buffer):
            data_buf = cl.Buffer(self.ctx, mf.READ_WRITE | mf.COPY_HOST_PTR, hostbuf=data)
        else:
            data_buf = data
        
        psumbytes = int(np.ceil(1.0*ndata/self.localSize)) * np.uint64(0).nbytes
        npsumbytes =  np.uint64(0).nbytes
        
        psum_buf = cl.Buffer(self.ctx, mf.READ_WRITE, psumbytes)
        npsum_buf = cl.Buffer(self.ctx, mf.READ_WRITE, npsumbytes)
        
        kernel = self.prg.prefixSumDownInplace
        kernel.set_args(data_buf, np.uint64(ndata), psum_buf, npsum_buf)
        
        global_dims = self.get_global(self.get_grid_dims(ndata))
        
        if e is None:
            e  = ( cl.enqueue_nd_range_kernel(self.queue, kernel, global_dims, self.localDims, wait_for=e), )
        else:
            e  = ( cl.enqueue_nd_range_kernel(self.queue, kernel, global_dims, self.localDims), )
        events += e
        
        npsum = np.zeros(1, dtype = np.uint64)
        events += (cl.enqueue_copy(self.queue, npsum, npsum_buf, wait_for=e),)
        
        if npsum>1:
            (e, psum_buf, psum1_buf, npsum1_buf, ndata2) = self.prefixSumDownInplace(e, psum_buf, npsum.item(), events)
        else:
            ndata2 = np.zeros(1, dtype = np.uint64)
            events += (cl.enqueue_copy(self.queue, ndata2, psum_buf, wait_for=e),)
            ndata2 = ndata2.item()
        
        self.prefixSumUp(e, data_buf, ndata, psum_buf, npsum, events)
        
        return (e, data_buf, psum_buf, npsum_buf, ndata2)
    
    def prefixSumUp(self, e, data, ndata, data2, ndata2, events):
        import numpy as np
        import pyopencl as cl
        mf = cl.mem_flags
        
        if not isinstance(data, cl.Buffer):
            data_buf = cl.Buffer(self.ctx, mf.READ_WRITE | mf.COPY_HOST_PTR, hostbuf=data)
        else:
            data_buf = data
        
        if not isinstance(data2, cl.Buffer):
            data2_buf = cl.Buffer(self.ctx, mf.READ_WRITE | mf.COPY_HOST_PTR, hostbuf=data2)
        else:
            data2_buf = data2
                
        kernel = self.prg.prefixSumUp
        kernel.set_args(data_buf, np.uint64(ndata), data2_buf, np.uint64(ndata2))
        
        global_dims = self.get_global(self.get_grid_dims(ndata))
        
        if e is None:
            e  = ( cl.enqueue_nd_range_kernel(self.queue, kernel, global_dims, self.localDims, wait_for=e), )
        else:
            e  = ( cl.enqueue_nd_range_kernel(self.queue, kernel, global_dims, self.localDims), )
        events += e
        
        return (e, data_buf, data2_buf)
    
    def filter(self, data, keys, low, hi, events):
        import numpy as np
        import pyopencl as cl
        mf = cl.mem_flags
        
        ndata = data.size
        
        (e, data_buf, keys_buf, indices_buf, bsum_buf, nbsum_buf, ndata2) = self.prefixSum(None, data, keys, ndata, low, hi, events)
        
        filt = np.zeros(ndata, dtype = np.bool8)
        indices = np.zeros(ndata, dtype = np.uint64)
        data2 = np.zeros(ndata2, dtype = PrefixSum.HOST_TYPE_DATA)
        keys2 = np.zeros(ndata2, dtype = PrefixSum.HOST_TYPE_KEYS)
        
        ndata2bytes = np.uint64(0).nbytes
        
        if PrefixSum.RETURN_FILTER == 1:
            filt_buf = cl.Buffer(self.ctx, mf.READ_WRITE, filt.nbytes)
        data2_buf = cl.Buffer(self.ctx, mf.READ_WRITE, data2.nbytes)
        keys2_buf = cl.Buffer(self.ctx, mf.READ_WRITE, keys2.nbytes)
        ndata2_buf = cl.Buffer(self.ctx, mf.READ_WRITE, ndata2bytes)
        
        low = PrefixSum.HOST_TYPE_KEYS(low)
        hi = PrefixSum.HOST_TYPE_KEYS(hi)

        kernel = self.prg.filter
        if PrefixSum.RETURN_FILTER == 1:
            kernel.set_args(data_buf, keys_buf, indices_buf, np.uint64(ndata), low, hi, filt_buf, data2_buf, keys2_buf, ndata2_buf)
        else:
            kernel.set_args(data_buf, keys_buf, indices_buf, np.uint64(ndata), low, hi, data2_buf, keys2_buf, ndata2_buf)
        
        global_dims = self.get_global(self.get_grid_dims(ndata))
        
        if e is None:
            e  = ( cl.enqueue_nd_range_kernel(self.queue, kernel, global_dims, self.localDims, wait_for=e), )
        else:
            e  = ( cl.enqueue_nd_range_kernel(self.queue, kernel, global_dims, self.localDims), )
        events += e
        
        if PrefixSum.RETURN_FILTER == 1:
            events += ( cl.enqueue_copy(self.queue, filt, filt_buf, wait_for=e), 
                        cl.enqueue_copy(self.queue, indices, indices_buf, wait_for=e),
                        cl.enqueue_copy(self.queue, data2, data2_buf, wait_for=e),
                        cl.enqueue_copy(self.queue, keys2, keys2_buf, wait_for=e) )
        else:
            events += ( cl.enqueue_copy(self.queue, indices, indices_buf, wait_for=e),
                        cl.enqueue_copy(self.queue, data2, data2_buf, wait_for=e),
                        cl.enqueue_copy(self.queue, keys2, keys2_buf, wait_for=e) )
        
        return (filt, indices, data2, keys2)

def listFile(FILE_NAME):
    ps = PrefixSum(fileName = FILE_NAME, localDims = (1,1,1), listFile = True)

def test(FILE_NAME, NDATA,LOCAL_DIMS):
    import numpy as np
    import pyopencl as cl
    
    ps = PrefixSum(fileName = FILE_NAME, localDims = LOCAL_DIMS)
    
    data = np.random.rand(NDATA).astype(PrefixSum.HOST_TYPE_DATA)
    keys = (np.random.rand(NDATA)*100).astype(PrefixSum.HOST_TYPE_KEYS)
    low = 33
    hi = 66
    
    events = []
    (filt, indices, data2, keys2) = ps.filter(data, keys, low, hi, events)
    
    # tests #
    print "\n\n*** NDATA = %d ***" % NDATA
    print "*** LOCAL_SIZE = %d ***" % ps.localSize
    print "*** TEST ***"
    if PrefixSum.RETURN_FILTER == 1:
        print "Filt:\t%d wrong" % ((keys>=33) & (keys < 66) != filt).sum()
        print "CumSum:\t%d wrong" % (filt.cumsum() != indices).sum()
    ########
    
    keysf = keys[(keys>=low) & (keys < hi)] ## filter keys on host
    if keysf.size != keys2.size:
        print "Result size unmatch"
    else:
        wrong = (keysf != keys2).sum() ## No of wrong items
        print "Result:\t%d wrong" % wrong 
        if wrong > 0:
            i = np.array(xrange(keys.size), dtype=np.int)
            err = i[keysf != keys2]
            print "Total:\t%d\nWrong:\nInd:\t%s\nKeys:\t%s\nKeys2:\t%s" % ( keys2.size, str(err), str(keys[keys[(keys>=33) & (keys < 66)] != keys2]), str(keys2[keys[(keys>=33) & (keys < 66)] != keys2]) )
    
    print "*** PROFILING INFO ***"
    print "Device:"
    d = ps.queue.get_info(cl.command_queue_info.DEVICE)
    info = [  cl.device_info.TYPE,
             cl.device_info.VENDOR, 
             cl.device_info.VERSION,
             cl.device_info.DRIVER_VERSION,
             cl.device_info.PLATFORM,
             cl.device_info.NAME,
             cl.device_info.LOCAL_MEM_SIZE,
             cl.device_info.LOCAL_MEM_TYPE,
             cl.device_info.MAX_COMPUTE_UNITS,
             cl.device_info.MAX_CLOCK_FREQUENCY,
             cl.device_info.MAX_CONSTANT_ARGS,
             cl.device_info.ADDRESS_BITS,
             cl.device_info.DOUBLE_FP_CONFIG,
             cl.device_info.ENDIAN_LITTLE,
             cl.device_info.GLOBAL_MEM_CACHE_SIZE,
             cl.device_info.GLOBAL_MEM_CACHE_TYPE,
             cl.device_info.GLOBAL_MEM_SIZE,
             cl.device_info.HOST_UNIFIED_MEMORY,
             cl.device_info.INTEGRATED_MEMORY_NV,
             cl.device_info.LOCAL_MEM_SIZE,
             cl.device_info.LOCAL_MEM_TYPE,
             cl.device_info.OPENCL_C_VERSION,
             cl.device_info.SINGLE_FP_CONFIG,
             cl.device_info.TYPE,
             cl.device_info.VENDOR,
             cl.device_info.WARP_SIZE_NV
    ]
    
    s = []
    for v in info:
        try: s += " * %s: %s" % (cl.device_info.to_string(v), str(d.get_info(v))),
        except Exception: pass
    print '\n'.join(s)
    print "\nExecution:"
    profiling = []
    t = 0
    for e in events:
        p = []
        p += e.get_profiling_info(cl.profiling_info.QUEUED),
        p += e.get_profiling_info(cl.profiling_info.SUBMIT),
        p += e.get_profiling_info(cl.profiling_info.START),
        p += e.get_profiling_info(cl.profiling_info.END),
        p += e.get_info(cl.event_info.COMMAND_TYPE),
        profiling += tuple(p),
        t += p[3] - p[2]
    print "Tot.time: %f ms" % (1E-6*t)
    d = ps.queue.get_info(cl.command_queue_info.DEVICE)
    for p in profiling:
        print " * %f ms (%s)" % (1E-6*(p[3] - p[2]), cl.command_type.to_string(p[4]))

if __name__ == '__main__':
    import sys
    args = []
    if len(sys.argv) > 1: args += sys.argv[1] ,
    else: args += 'kernels.cl',
    
    if len(sys.argv) > 2: 
        if sys.argv[2] == 'list': 
            listFile(sys.argv[1])
            sys.exit(0)
        else: args += int(sys.argv[2]) ,
    else: args += int(np.exp2(23)) + 101 ,
        
    if len(sys.argv) > 3: args += (int(sys.argv[3]), 1, 1) ,
    else: args += (64,1,1) ,
        
    test(*args)

