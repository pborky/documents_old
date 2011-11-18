#!/usr/bin/python

import pyopencl as cl
import numpy as np
import io

mf = cl.mem_flags

ctx = cl.create_some_context(interactive=False, answers=0)
queue = cl.CommandQueue(ctx)

HOST_TYPE_DATA = np.float32
HOST_TYPE_KEY = np.uint32

GPU_TYPE_DATA = 'float'
GPU_TYPE_KEYS = 'uint'

NDATA =  16777216 #2048

LOCAL_DIMS = (16, 16, 1)
LOCAL_SIZE = np.prod(LOCAL_DIMS)

SERIAL_COUNT = 1
GRID_DIMS = (int(np.ceil(np.ceil(1.0*NDATA/LOCAL_SIZE)/SERIAL_COUNT)), 1, 1)
CACHE_SIZE = np.prod(GRID_DIMS)

subs = {
    'LOCAL_SIZE':   LOCAL_SIZE,
    'TYPE_DATA':    GPU_TYPE_DATA,
    'TYPE_KEYS':    GPU_TYPE_KEYS,
}

get_global = lambda grid, local: (grid[0]*local[0], grid[1]*local[1], grid[2]*local[2])

f = io.open('kernels.cl')
try: lines = f.readlines()
finally: f.close()

src = ''.join(lines) % subs
print src
prg = cl.Program(ctx, src).build()

filterPrepare = prg.filterPrepare
filter = prg.filter
prefixSumUp = prg.prefixSumUp
prefixSumDown = prg.prefixSumDown

data = np.random.rand(NDATA).astype(HOST_TYPE_DATA)
keys = (np.random.rand(NDATA)*100).astype(HOST_TYPE_KEY)
filtbool = np.zeros(NDATA).astype(np.bool8)
filtdata = np.zeros(NDATA).astype(np.uint64)

data_buf = cl.Buffer(ctx, mf.READ_ONLY, data.nbytes)
keys_buf = cl.Buffer(ctx, mf.READ_ONLY, keys.nbytes)
filtbool_buf = cl.Buffer(ctx, mf.READ_WRITE, filtbool.nbytes)
filtdata_buf = cl.Buffer(ctx, mf.READ_WRITE, filtdata.nbytes)

e  = [ cl.enqueue_copy(queue, data_buf, data), cl.enqueue_copy(queue, keys_buf, keys), ]

filterPrepare.set_args(data_buf, keys_buf, np.uint64(NDATA), np.uint32(33), np.uint32(66), filtbool_buf, filtdata_buf)

e  = [ cl.enqueue_nd_range_kernel(queue, filterPrepare, get_global(GRID_DIMS, LOCAL_DIMS), LOCAL_DIMS, wait_for=e), ]

e  = [ cl.enqueue_copy(queue, filtbool, filtbool_buf, wait_for=e), ]

print "%d wrong items" % ((keys>=33) & (keys < 66) != filtbool).sum()

psumdata = np.zeros(np.prod(GRID_DIMS)).astype(np.uint64)
psumndata = np.array([np.prod(GRID_DIMS),], dtype=np.uint64)

psumdata_buf = cl.Buffer(ctx, mf.READ_WRITE, psumdata.nbytes)
psumndata_buf = cl.Buffer(ctx, mf.READ_WRITE, psumndata.nbytes)

prefixSumDown.set_args(filtdata_buf, np.uint64(NDATA), psumdata_buf, psumndata_buf)

e  = [ cl.enqueue_nd_range_kernel(queue, prefixSumDown, get_global(GRID_DIMS, LOCAL_DIMS), LOCAL_DIMS, wait_for=e), ]

e  = [ cl.enqueue_copy(queue, psumndata, psumndata_buf, wait_for=e), ]
cl.enqueue_copy(queue, filtdata, filtdata_buf, wait_for=e)
filtdata[:256]

GRID_DIMS = (int(np.ceil(np.ceil(1.0*psumndata/LOCAL_SIZE)/SERIAL_COUNT)), 1, 1)
psumdata2 = np.zeros(np.prod(GRID_DIMS)).astype(np.uint64)
psumndata2 = np.array([0,], dtype=np.uint64)

psumdata2_buf = cl.Buffer(ctx, mf.READ_WRITE, psumdata2.nbytes)
psumndata2_buf = cl.Buffer(ctx, mf.READ_WRITE, psumndata2.nbytes)

prefixSumDown.set_args(psumdata_buf, np.uint64(psumndata), psumdata2_buf, psumndata2_buf)

e  = [ cl.enqueue_nd_range_kernel(queue, prefixSumDown, get_global(GRID_DIMS, LOCAL_DIMS), LOCAL_DIMS), ]

e  = [ cl.enqueue_copy(queue, psumndata2, psumndata2_buf, wait_for=e), ]

prefixSumUp.set_args(psumdata_buf, np.uint64(psumndata), psumdata2_buf, np.uint64(psumndata2))

GRID_DIMS = (int(np.ceil(np.ceil(1.0*psumndata/LOCAL_SIZE)/SERIAL_COUNT)), 1, 1)

e  = [ cl.enqueue_nd_range_kernel(queue, prefixSumUp, get_global(GRID_DIMS, LOCAL_DIMS), LOCAL_DIMS, wait_for=e), ]

prefixSumUp.set_args(filtdata_buf, np.uint64(NDATA), psumdata_buf, np.uint64(psumndata))

GRID_DIMS = (int(np.ceil(np.ceil(1.0*NDATA/LOCAL_SIZE)/SERIAL_COUNT)), 1, 1)

e  = [ cl.enqueue_nd_range_kernel(queue, prefixSumUp, get_global(GRID_DIMS, LOCAL_DIMS), LOCAL_DIMS, wait_for=e), ]



