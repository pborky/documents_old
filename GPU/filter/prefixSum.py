#!/usr/bin/python

import pyopencl as cl
import numpy as np

mf = cl.mem_flags

ctx = cl.create_some_context(interactive=False, answers=0)
queue = cl.CommandQueue(ctx)


NDATA =  16777216 #2048

LOCAL_DIMS = (16, 16, 1)
LOCAL_SIZE = np.prod(LOCAL_DIMS)

SERIAL_COUNT = 1
GRID_DIMS = (int(np.ceil(np.ceil(1.0*NDATA/LOCAL_SIZE)/SERIAL_COUNT)), 1, 1)
CACHE_SIZE = np.prod(GRID_DIMS)

get_global = lambda grid, local: (grid[0]*local[0], grid[1]*local[1], grid[2]*local[2])


data = (np.random.rand(NDATA)>.5).astype(np.uint32)

data_buf = cl.Buffer(ctx, mf.READ_ONLY, data.nbytes)

SRC = '''//CL//
global uint cache_g [%(CACHE_SIZE)d];
kernel void sum (
    global uint *data,
    const uint ndata,
    const uint lid,
    const uint bid,
    const uint bsize,
    const uint bcount,
    global uint *nres
) {
}
kernel void prefixSum (
    global const uint *data,
    const uint ndata,
    global uint *result,
    global uint *nresult
) {    
    private size_t bsize = get_local_size(0)*get_local_size(1)*get_local_size(2);
    private size_t bcount = get_num_groups(0)*get_num_groups(1)*get_num_groups(2);
    
    private size_t lid = get_local_id(0) + get_local_size(0)*(get_local_id(1) + get_local_size(1)*get_local_id(2));
    private size_t bid = get_group_id(0) + get_num_groups(0)*(get_group_id(1) + get_num_groups(1)*get_group_id(2));
    
    local uint data_l[%(LOCAL_SIZE)d];
    private uint data_p = data[lid+bid*bize];
    data_l[lid] = data_p;
    barrier(CLK_LOCAL_MEM_FENCE);
    for (size_t i = 1; i < bsize>>1; i<<=1 ) {
        if (lid >= i) {
            data_p += data_l[lid-1];
        }
        barrier(CLK_LOCAL_MEM_FENCE);
        if (lid >= i) {
            data_l[lid] = data_p;
        }
        barrier(CLK_LOCAL_MEM_FENCE);
    }
    if (lid == bsize - 1) {
        data_g[bid] = data_p; 
    }
    barrier(CLK_GLOBAL_MEM_FENCE);
    prefixSum(data_g, bcount, );
}
'''


