#!/usr/bin/python

import pyopencl as cl
import numpy as np
import numpy.linalg as la

mf = cl.mem_flags

ctx = cl.create_some_context(interactive=False, answers=0)
queue = cl.CommandQueue(ctx)

HOST_TYPE = np.float32
GPU_TYPE = 'float'
NDATA =  16777216 #2048
LOCAL_DIMS = (16, 16, 1)
LOCAL_SIZE = np.prod(LOCAL_DIMS)
SERIAL_COUNT = 4
GRID_DIMS = (int(np.ceil(np.ceil(1.0*NDATA/LOCAL_SIZE)/SERIAL_COUNT)), 1, 1)
CACHE_SIZE = np.prod(GRID_DIMS)

get_global = lambda grid, local: (grid[0]*local[0], grid[1]*local[1], grid[2]*local[2])

a = np.random.rand(NDATA).astype(HOST_TYPE)
b = np.random.rand(NDATA).astype(HOST_TYPE)
c = np.zeros(CACHE_SIZE).astype(HOST_TYPE)
d = np.zeros(1).astype(HOST_TYPE)
n = np.zeros(1).astype(np.uint32)

a_buf = cl.Buffer(ctx, mf.READ_ONLY, a.nbytes)
b_buf = cl.Buffer(ctx, mf.READ_ONLY, b.nbytes)
c_buf = cl.Buffer(ctx, mf.READ_WRITE, c.nbytes)
d_buf = cl.Buffer(ctx, mf.READ_WRITE, d.nbytes)
n_buf = cl.Buffer(ctx, mf.READ_WRITE, n.nbytes)

SRC = """//CL//
kernel void sum (
    global %(TYPE)s         *c, // partial product [nc x 1]
    global %(TYPE)s         *d, // result
    const uint              nc, // size of c
    global uint             *n  // size of d
) {
    local %(TYPE)s cache_l [%(LOCAL_SIZE)d];
    
    private size_t bsize = get_local_size(0)*get_local_size(1)*get_local_size(2);
    private size_t bcount = get_num_groups(0)*get_num_groups(1)*get_num_groups(2);
    
    private size_t lid = get_local_id(0) + get_local_size(0)*(get_local_id(1) + get_local_size(1)*get_local_id(2));
    private size_t bid = get_group_id(0) + get_num_groups(0)*(get_group_id(1) + get_num_groups(1)*get_group_id(2));
    
    private %(TYPE)s cache_p = 0;
    for (size_t i = lid+bid*bsize; i < nc; i += bsize * bcount) {
        cache_p += c[i];
    }
    cache_l[lid] = cache_p;
    for (uint k = bsize>>1; k > 0; k >>=1) {
        barrier(CLK_LOCAL_MEM_FENCE);
        if (lid < k) {
            cache_l[lid] += cache_l[lid+k];
        }
    }
    if (lid == 0) {
        c[bid] = cache_l[0];
        if (lid == 0 && bid == 0) {
            *n = bcount;
            *d = cache_l[0];
        }
    }
}"""
SRC += """//CL//
kernel void product (
    global const %(TYPE)s   *a, // vector a [n x 1]
    global const %(TYPE)s   *b, // vector b [n x 1]
    global %(TYPE)s         *c, // partial products [n x 1]
    const uint              nab,// size of a and b
    global uint             *n  // size of c
) {
    local %(TYPE)s cache_l [%(LOCAL_SIZE)d];
    
    private size_t bsize = get_local_size(0)*get_local_size(1)*get_local_size(2);
    private size_t bcount = get_num_groups(0)*get_num_groups(1)*get_num_groups(2);
    
    private size_t lid = get_local_id(0) + get_local_size(0)*(get_local_id(1) + get_local_size(1)*get_local_id(2));
    private size_t bid = get_group_id(0) + get_num_groups(0)*(get_group_id(1) + get_num_groups(1)*get_group_id(2));
    
    private %(TYPE)s cache_p = 0;
    for (size_t i = lid+bid*bsize; i < nab; i += bsize*bcount) {
        cache_p += a[i]*b[i];
    }
    cache_l[lid] = cache_p;
    for (uint k = bsize>>1; k > 0; k >>=1) {
        barrier(CLK_LOCAL_MEM_FENCE);
        if (lid < k) {
            cache_l[lid] += cache_l[lid+k];
        }
    }
    if (lid == 0) {
        c[bid] = cache_l[0];
        if (bid == 0) {
            *n = bcount;
        }
    }
}
"""

SRC = SRC % {
    'LOCAL_SIZE':   LOCAL_SIZE,
    'TYPE':         GPU_TYPE,
    'CACHE_SIZE':   CACHE_SIZE
}

print SRC

prg = cl.Program(ctx, SRC).build()

product = prg.product
sum = prg.sum

product.set_args(a_buf, b_buf, c_buf, np.uint32(0), n_buf)
sum.set_args(c_buf, d_buf, np.uint32(0), n_buf)

e  = [ cl.enqueue_copy(queue, a_buf, a), ]
e += [ cl.enqueue_copy(queue, b_buf, b), ]

product.set_arg(3, np.uint32(NDATA))
e  = [ cl.enqueue_nd_range_kernel(queue, product, get_global(GRID_DIMS, LOCAL_DIMS), LOCAL_DIMS, wait_for=e), ]

cl.enqueue_copy(queue, n, n_buf, wait_for=e)
cl.enqueue_copy(queue, c, c_buf, wait_for=e)
print c[:n.item()].sum()
while n > 1:
    GRID_DIMS = (int(np.ceil(np.ceil(1.0*n.item()/LOCAL_SIZE)/SERIAL_COUNT)), 1, 1)
    sum.set_arg(2, np.uint32(n.item()))
    e = [ cl.enqueue_nd_range_kernel(queue, sum, get_global(GRID_DIMS, LOCAL_DIMS), LOCAL_DIMS), ]
    cl.enqueue_copy(queue, n, n_buf, wait_for=e)
    cl.enqueue_copy(queue, c, c_buf, wait_for=e)
    print c[:n.item()].sum()

cl.enqueue_copy(queue, d, d_buf, wait_for=e)

print d.item()
print np.dot(a,b)
print (np.dot(a,b) - d.item()) / d.item()

