#!/usr/bin/python

import pyopencl as cl
import numpy as np
import numpy.linalg as la

mf = cl.mem_flags

ctx = cl.create_some_context(interactive=False, answers=0)
queue = cl.CommandQueue(ctx)

HOST_TYPE = np.float32
GPU_TYPE = 'float'

NDATA = 16777216 #2048
LOCAL_SIZE = (8, 8, 8)
GLOBAL_SIZE = (int(np.ceil(1.0*NDATA/(LOCAL_SIZE[1]*LOCAL_SIZE[2]))), LOCAL_SIZE[1], LOCAL_SIZE[2])
CACHE_SIZE = long(HOST_TYPE(0).nbytes * NDATA / np.prod(LOCAL_SIZE))

SRC = """//CL//
kernel void dot_prod (
        global const %(TYPE)s *a,   // vector a [n x 1]
        global const %(TYPE)s *b,   // vector b [n x 1]
        global %(TYPE)s *c,         // dot product result [1 x 1]
        const uint n,               // size of a and b
        global %(TYPE)s *cache      // global cache [cache_size x 1]
) {
    size_t bsize = get_local_size(0)*get_local_size(1)*get_local_size(2);
    size_t bcount = get_num_groups(0)*get_num_groups(1)*get_num_groups(2);
    size_t lid = get_local_id(0) + get_local_size(0)*(get_local_id(1) + get_local_size(1)*get_local_id(2));
    size_t bid = get_group_id(0) + get_num_groups(0)*(get_group_id(1) + get_num_groups(1)*get_group_id(2));
    
    local %(TYPE)s prod_l[%(LOCAL_SIZE)d];
    /*global %(TYPE)s test [%(CACHE_SIZE)d];*/
    prod_l[lid] = ((lid+bid*bsize) >= n) ? 0 : (a[lid+bid*bsize] * b[lid+bid*bsize]);
    for (size_t k = bsize>>1; k > 0; k >>=1) {
        barrier(CLK_LOCAL_MEM_FENCE);
        if (lid < k) {
            prod_l[lid] += prod_l[lid+k];
        }
    }
    if (lid == 0) {
        cache[bid] = prod_l[0];
    }
    size_t l,reduced_size;
    for (l = reduced_size = bcount/bsize;; reduced_size = l, l /= bsize) {
        if (l > 0 && bid >= l) break;
        if (l == 0 && bid > 0) break;
        
        barrier(CLK_GLOBAL_MEM_FENCE);
        prod_l[lid] = (l == 0 && lid >= reduced_size) ? 0 : cache[lid+bid*bsize];
        for (size_t k = bsize>>1; k > 0; k >>=1) {
            barrier(CLK_LOCAL_MEM_FENCE);
            if (lid < k) {
                prod_l[lid] += prod_l[lid+k];
            }
        }
        if (lid == 0) {
            if (l > 1) {
                cache[bid] = prod_l[0];
            } else {
                c[0] = prod_l[0];
            }
        }
        
        if (l <= 1) break;
    }
}
""" % { 
    'LOCAL_SIZE': np.prod(LOCAL_SIZE), 
    'TYPE': GPU_TYPE, 
    'CACHE_SIZE': CACHE_SIZE
}

print SRC

prg = cl.Program(ctx, SRC).build()
kernel = prg.dot_prod

a = np.random.rand(NDATA).astype(HOST_TYPE)
b = np.random.rand(NDATA).astype(HOST_TYPE)
c = np.array(0).astype(HOST_TYPE)
x = np.zeros(CACHE_SIZE).astype(HOST_TYPE)

a_buf = cl.Buffer(ctx, mf.READ_ONLY | mf.COPY_HOST_PTR, hostbuf=a)
b_buf = cl.Buffer(ctx, mf.READ_ONLY | mf.COPY_HOST_PTR, hostbuf=b)
c_buf = cl.Buffer(ctx, mf.WRITE_ONLY, c.nbytes)
cache = cl.Buffer(ctx, mf.WRITE_ONLY, x.nbytes)

kernel.set_args(a_buf, b_buf, c_buf, np.uint32(NDATA), cache)
e = cl.enqueue_nd_range_kernel(queue, kernel, GLOBAL_SIZE, LOCAL_SIZE)

cl.enqueue_copy(queue, c, c_buf, wait_for=(e,))

cl.enqueue_copy(queue, x, cache, wait_for=(e,))

print (c - np.dot(a,b)) / c
print (x[0]-np.dot(a,b))/x[0]

