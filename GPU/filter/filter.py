#!/usr/bin/python

class PrefixSum:
    import numpy as np
    HOST_TYPE_DATA = np.float32
    HOST_TYPE_KEY = np.uint32
    
    GPU_TYPE_DATA = 'float'
    GPU_TYPE_KEYS = 'uint'
            
    LOCAL_DIMS = (16, 16, 1)
    LOCAL_SIZE = np.prod(LOCAL_DIMS)
    
    FILE_NAME = 'kernels.cl'
    
    def get_grid_dims(self, ndata):
        return (int(np.ceil(1.0*ndata/PrefixSum.LOCAL_SIZE)), 1, 1)
    
    def get_global(self, grid):
        return (grid[0]*PrefixSum.LOCAL_DIMS[0], grid[1]*PrefixSum.LOCAL_DIMS[1], grid[2]*PrefixSum.LOCAL_DIMS[2])
    
    def __init__(self, fileName = FILE_NAME):
        import pyopencl as cl
        import numpy as np
        import io
        
        mf = cl.mem_flags
        
        self.ctx = cl.create_some_context(interactive=False, answers=0)
        self.queue = cl.CommandQueue(self.ctx)
        
        f = io.open('kernels.cl')
        try: lines = f.readlines()
        finally: f.close()
        
        src = ''.join(lines) % { 'LOCAL_SIZE': PrefixSum.LOCAL_SIZE, 'TYPE_DATA':PrefixSum.GPU_TYPE_DATA,'TYPE_KEYS':PrefixSum.GPU_TYPE_KEYS }
        #print src
        self.prg = cl.Program(self.ctx, src).build()

    def filterPrepare(self, data, keys):
        import numpy as np
        import pyopencl as cl
        mf = cl.mem_flags
        
        ndata = data.size
        if keys.size != ndata: raise Exception()
        
        filtbytes = np.bool8(False).nbytes * ndata
        
        data_buf = cl.Buffer(self.ctx, mf.READ_ONLY, data.nbytes)
        keys_buf = cl.Buffer(self.ctx, mf.READ_ONLY, keys.nbytes)
        filt_buf = cl.Buffer(self.ctx, mf.READ_WRITE, filtbytes)
        
        e  = [  cl.enqueue_copy(self.queue, data_buf, data), 
                cl.enqueue_copy(self.queue, keys_buf, keys), ]
        
        kernel = self.prg.filterPrepare
        kernel.set_args(data_buf, keys_buf, np.uint64(ndata), np.uint32(33), np.uint32(66), filt_buf)
        global_dims = self.get_global(self.get_grid_dims(ndata))
        e  = [ cl.enqueue_nd_range_kernel(self.queue, kernel, global_dims, PrefixSum.LOCAL_DIMS, wait_for=e), ]
        
        return (e, data_buf, keys_buf, filt_buf)

    def prefixSumDown(self, e, filt, ndata):
        import numpy as np
        import pyopencl as cl
        mf = cl.mem_flags
        
        if not isinstance(filt, cl.Buffer):
            filt_buf = cl.Buffer(self.ctx, mf.READ_ONLY | mf.COPY_HOST_PTR, hostbuf= filt)
        else:
            filt_buf = filt
        
        databytes = ndata * np.uint64(0).nbytes
        psumbytes = int(np.ceil(1.0*ndata/PrefixSum.LOCAL_SIZE)) * np.uint64(0).nbytes
        npsumbytes =  np.uint64(0).nbytes
        
        data_buf = cl.Buffer(self.ctx, mf.READ_WRITE, databytes)
        psum_buf = cl.Buffer(self.ctx, mf.READ_WRITE, psumbytes)
        npsum_buf = cl.Buffer(self.ctx, mf.READ_WRITE, npsumbytes)
        
        kernel = self.prg.prefixSumDown
        kernel.set_args(filt_buf, data_buf, np.uint64(ndata), psum_buf, npsum_buf)
        
        global_dims = self.get_global(self.get_grid_dims(ndata))
        
        if e is None:
            e  = ( cl.enqueue_nd_range_kernel(self.queue, kernel, global_dims, PrefixSum.LOCAL_DIMS, wait_for=e), )
        else:
            e  = ( cl.enqueue_nd_range_kernel(self.queue, kernel, global_dims, PrefixSum.LOCAL_DIMS), )
        
        return (e, data_buf, psum_buf, npsum_buf)
    
    def prefixSumDownInplace(self, e, data, ndata):
        import numpy as np
        import pyopencl as cl
        mf = cl.mem_flags
        
        if not isinstance(data, cl.Buffer):
            data_buf = cl.Buffer(self.ctx, mf.READ_WRITE | mf.COPY_HOST_PTR, hostbuf=data)
        else:
            data_buf = data
        
        psumbytes = int(np.ceil(1.0*ndata/PrefixSum.LOCAL_SIZE)) * np.uint64(0).nbytes
        npsumbytes =  np.uint64(0).nbytes
        
        psum_buf = cl.Buffer(self.ctx, mf.READ_WRITE, psumbytes)
        npsum_buf = cl.Buffer(self.ctx, mf.READ_WRITE, npsumbytes)
        
        kernel = self.prg.prefixSumDownInplace
        kernel.set_args(data_buf, np.uint64(ndata), psum_buf, npsum_buf)
        
        global_dims = self.get_global(self.get_grid_dims(ndata))
        
        if e is None:
            e  = ( cl.enqueue_nd_range_kernel(self.queue, kernel, global_dims, PrefixSum.LOCAL_DIMS, wait_for=e), )
        else:
            e  = ( cl.enqueue_nd_range_kernel(self.queue, kernel, global_dims, PrefixSum.LOCAL_DIMS), )
        
        return (e, data_buf, psum_buf, npsum_buf)
    
    def prefixSumUp(self, e, data, ndata, data2, ndata2):
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
            e  = ( cl.enqueue_nd_range_kernel(self.queue, kernel, global_dims, PrefixSum.LOCAL_DIMS, wait_for=e), )
        else:
            e  = ( cl.enqueue_nd_range_kernel(self.queue, kernel, global_dims, PrefixSum.LOCAL_DIMS), )
        
        return (e, data_buf, data2_buf)
    
    def filter(self, e, data, keys, filt, indices, ndata, ndata2):
        import numpy as np
        import pyopencl as cl
        mf = cl.mem_flags
        
        if not isinstance(data, cl.Buffer):
            data_buf = cl.Buffer(self.ctx, mf.READ_ONLY | mf.COPY_HOST_PTR, hostbuf=data)
        else:
            data_buf = data
        
        if not isinstance(keys, cl.Buffer):
            keys_buf = cl.Buffer(self.ctx, mf.READ_ONLY | mf.COPY_HOST_PTR, hostbuf=keys)
        else:
            keys_buf = keys
        
        if not isinstance(filt, cl.Buffer):
            filt_buf = cl.Buffer(self.ctx, mf.READ_ONLY | mf.COPY_HOST_PTR, hostbuf=filt)
        else:
            filt_buf = filt
        
        if not isinstance(indices, cl.Buffer):
            indices_buf = cl.Buffer(self.ctx, mf.READ_ONLY | mf.COPY_HOST_PTR, hostbuf=indices)
        else:
            indices_buf = indices
        
        data2bytes = ndata2 * np.uint64(0).nbytes
        keys2bytes = ndata2 * np.uint64(0).nbytes
        ndata2bytes = np.uint64(0).nbytes
        
        data2_buf = cl.Buffer(self.ctx, mf.READ_WRITE, data2bytes)
        keys2_buf = cl.Buffer(self.ctx, mf.READ_WRITE, keys2bytes)
        ndata2_buf = cl.Buffer(self.ctx, mf.READ_WRITE, ndata2bytes)
        
        kernel = self.prg.filter
        kernel.set_args(data_buf, keys_buf, filt_buf, indices_buf, np.uint64(ndata), data2_buf, keys2_buf, ndata2_buf)
        
        global_dims = self.get_global(self.get_grid_dims(ndata))
        
        if e is None:
            e  = ( cl.enqueue_nd_range_kernel(self.queue, kernel, global_dims, PrefixSum.LOCAL_DIMS, wait_for=e), )
        else:
            e  = ( cl.enqueue_nd_range_kernel(self.queue, kernel, global_dims, PrefixSum.LOCAL_DIMS), )
        
        return (e, data2_buf, keys2_buf, ndata2_buf)

if __name__ == '__main__':
    import numpy as np
    import pyopencl as cl
    
    ps = PrefixSum()
    
    NDATA = int(np.exp2(20))
    
    data = np.random.rand(NDATA).astype(PrefixSum.HOST_TYPE_DATA)
    keys = (np.random.rand(NDATA)*100).astype(PrefixSum.HOST_TYPE_KEY)
    
    (e, data_buf, keys_buf, filt_buf) = ps.filterPrepare(data, keys)
    
    filt = np.zeros(NDATA, dtype = np.bool8)
    cl.enqueue_copy(ps.queue, filt, filt_buf, wait_for=e)
    
    # test #
    print "Filt:\t%d wrong" % ((keys>=33) & (keys < 66) != filt).sum()
    ########
    
    (e, psum1_buf, psum2_buf, npsum2_buf) = ps.prefixSumDown(e, filt_buf, NDATA)
    npsum2 = np.zeros(1, dtype = np.uint64)
    cl.enqueue_copy(ps.queue, npsum2, npsum2_buf, wait_for=e)
    if npsum2 > 1:
        (e, psum2_buf, psum3_buf, npsum3_buf) = ps.prefixSumDownInplace(e, psum2_buf, npsum2.item())
        npsum3 = np.zeros(1, dtype = np.uint64)
        cl.enqueue_copy(ps.queue, npsum3, npsum3_buf, wait_for=e)
        if npsum3 > 1:
            (e, psum3_buf, psum4_buf, npsum4_buf) = ps.prefixSumDownInplace(e, psum3_buf, npsum3.item())
            npsum4 = np.zeros(1, dtype = np.uint64)
            psum4 = np.zeros(1, dtype = np.uint64)
            cl.enqueue_copy(ps.queue, npsum4, npsum4_buf, wait_for=e)
            cl.enqueue_copy(ps.queue, psum4, psum4_buf, wait_for=e)
            (e, psum3_buf, psum4_buf) = ps.prefixSumUp(e, psum3_buf, npsum3.item(), psum4_buf, npsum4.item())
        (e, psum2_buf, psum3_buf) = ps.prefixSumUp(e, psum2_buf, npsum2.item(), psum3_buf, npsum3.item())
    (e, psum1_buf, psum2_buf) = ps.prefixSumUp(e, psum1_buf, NDATA, psum2_buf, npsum2.item())
    (e, data2_buf, keys2_buf, ndata2_buf) = ps.filter(e, data_buf, keys_buf, filt_buf, psum1_buf, NDATA, psum4.item())
    
    psum1 = np.zeros(NDATA, dtype = np.uint64)
    ndata2 = np.zeros(1, dtype = np.uint64)
    data2 = np.zeros(psum4.item(), dtype = PrefixSum.HOST_TYPE_DATA)
    keys2 = np.zeros(psum4.item(), dtype = PrefixSum.HOST_TYPE_KEY)
    
    cl.enqueue_copy(ps.queue, psum1, psum1_buf, wait_for=e)
    cl.enqueue_copy(ps.queue, ndata2, ndata2_buf, wait_for=e)
    cl.enqueue_copy(ps.queue, data2, data2_buf, wait_for=e)
    cl.enqueue_copy(ps.queue, keys2, keys2_buf, wait_for=e)
    
    # test #
    print "CumSum:\t%d wrong" % (filt.cumsum() != psum1).sum()
    ########
    
    keysf = keys[(keys>=33) & (keys < 66)]
    if keysf.size != keys2.size:
        print "Result size unmatch"
    else:
        wrong = (keys[(keys>=33) & (keys < 66)] != keys2).sum()
        print "Result:\t%d wrong" % wrong
        if wrong > 0:
            i = np.array(xrange(keys.size), dtype=np.int)
            err = i[keys[(keys>=33) & (keys < 66)] != keys2]
            print "Total:\t%d\nWrong:\nInd:\t%s\nKeys:\t%s\nKeys2:\t%s" % ( keys2.size, str(err), str(keys[keys[(keys>=33) & (keys < 66)] != keys2]), str(keys2[keys[(keys>=33) & (keys < 66)] != keys2]) )
