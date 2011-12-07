#define BSIZE (get_local_size(0))
#define BCOUNT (get_num_groups(0))
#define LID (get_local_id(0))
#define BID (get_group_id(0))
#define GID (LID + (BID * BSIZE))
#define FILTER(key,low,hi) ((key >= low) && (key < hi))

kernel void prefixSumDown (
    global const DATA_T *   data,
    global const KEYS_T *   keys,
    const ulong             ndata,
    const KEYS_T            low,
    const KEYS_T            hi,
    global ulong *          psum,
    global ulong *          bsum,
    global ulong *          nbsum
) {
    private size_t bsize, lid, gid;
    lid = (LID)<<1;
    gid = (GID)<<1;
    bsize = (BSIZE)<<1;
    
    local ulong psum_l [LSIZE<<1+1];
    
    if (gid+1 < ndata) {
        private KEYS_T key_p = keys[gid];
        psum_l[lid] = FILTER(key_p, low, hi) ? 1:0;
        key_p = keys[gid+1];
        psum_l[lid+1] = FILTER(key_p, low, hi) ? 1:0;
    } else if (gid < ndata)  {
        private KEYS_T key_p = keys[gid];
        psum_l[lid] = FILTER(key_p, low, hi) ? 1:0;
        psum_l[lid+1] = 0;
    } else {
        psum_l[lid] = 0;
        psum_l[lid+1] = 0;
    }
    
    int offset = 1;
    for ( size_t d = bsize>>1; d > 0 ; d >>= 1, offset <<= 1 ) {
        barrier(CLK_LOCAL_MEM_FENCE);
        if (lid>>1 < d) {
            psum_l[offset*(lid+2)-1] += psum_l[offset*(lid+1)-1];
        }
    }
    if (lid == 0) {
        psum_l[bsize] = psum_l[bsize-1];
        psum_l[bsize-1] = 0;
    }
    offset >>= 1;
    for ( size_t d = 1; d < bsize; d <<= 1, offset >>= 1 ) {
        barrier(CLK_LOCAL_MEM_FENCE);
        if ( lid>>1 < d ) {
            int ai = offset*(lid+1)-1;
            int bi = offset*(lid+2)-1;

            ulong t = psum_l[ai];
            psum_l[ai] = psum_l[bi];
            psum_l[bi] += t;
        }
    }
    barrier(CLK_LOCAL_MEM_FENCE);
    if (gid+1 < ndata) {
        psum[gid] = psum_l[lid+1];
        psum[gid+1] = psum_l[lid+2];
    } else if (gid < ndata) {
        psum[gid] = psum_l[lid+1];
    }
    
    if (lid == 0)   bsum[BID] = psum_l[bsize];
    if (gid == 0)   *nbsum = ((BCOUNT)>>1)+((BCOUNT)&1);
}

kernel void prefixSumDownInplace (
    global ulong *          data,
    const ulong             ndata,
    global ulong *          psum,
    global ulong *          npsum
) {
    private ulong bsize, lid, gid;
    lid = (LID)<<1;
    gid = (GID)<<1;
    bsize = (BSIZE)<<1;
    
    local ulong psum_l [LSIZE<<1+1];
    
    if (gid+1 < ndata) {
        psum_l[lid] = data[gid];
        psum_l[lid+1] = data[gid+1];
    } else if (gid < ndata)  {
        psum_l[lid] = data[gid];
        psum_l[lid+1] = 0;
    } else {
        psum_l[lid] = 0;
        psum_l[lid+1] = 0;
    }
    
    int offset = 1;
    for ( size_t d = bsize>>1; d > 0 ; d >>= 1, offset <<= 1 ) {
        barrier(CLK_LOCAL_MEM_FENCE);
        if (lid>>1 < d) {
            psum_l[offset*(lid+2)-1] += psum_l[offset*(lid+1)-1];
        }
    }
    if (lid == 0) {
        psum_l[bsize] = psum_l[bsize-1];
        psum_l[bsize-1] = 0;
    }
    offset >>= 1;
    for ( size_t d = 1; d < bsize; d <<= 1, offset >>= 1 ) {
        barrier(CLK_LOCAL_MEM_FENCE);
        if ( lid>>1 < d ) {
            int ai = offset*(lid+1)-1;
            int bi = offset*(lid+2)-1;

            ulong t = psum_l[ai];
            psum_l[ai] = psum_l[bi];
            psum_l[bi] += t;
        }
    }
    barrier(CLK_LOCAL_MEM_FENCE);
    
    if (gid+1 < ndata) {
        data[gid] = psum_l[lid+1];
        data[gid+1] = psum_l[lid+2];
    } else if (gid < ndata) {
        data[gid] = psum_l[lid+1];
    }
    if (lid == 0) psum[BID] = psum_l[bsize];
    if (gid == 0) *npsum = ((BCOUNT)>>1)+((BCOUNT)&1);
}

kernel void prefixSumUp (
    global ulong *              data,
    const ulong                 ndata,
    global ulong *              psum,
    const ulong                 npsum
) {
    private ulong bid, gid;
    bid = BID;
    gid = (GID + BSIZE)<<1;
    bool first = LID == 0;
    
    local ulong psum_l;
    
    if (first) {
        psum_l = (bid < npsum) ? psum[bid] : 0;
    }
    barrier(CLK_LOCAL_MEM_FENCE);
    if (gid < ndata) {
        data[gid] += psum_l;
    } 
    
    bid += BCOUNT;
    gid += BCOUNT*BSIZE;
    
    if (first) {
        psum_l = (bid < npsum) ? psum[bid] : 0;
    }
    barrier(CLK_LOCAL_MEM_FENCE);
    if (gid < ndata) {
        data[gid] += psum_l;
    }
}

kernel void filter (
    global const DATA_T *   data,
    global const KEYS_T *   keys,
    global const ulong  *   indices,
    const ulong             ndata,
    const KEYS_T            low,
    const KEYS_T            hi,
#if RETURN_FILTER == 1
    global bool *           filt,
#endif
    global DATA_T *         dataout,
    global KEYS_T *         keysout,
    global ulong *          ndataout
) {
    private ulong gid = GID;
    
    for (ulong gid = GID; gid < ndata; gid += BCOUNT*BSIZE) {
        private KEYS_T key_p = keys[gid];
        private bool filt_p = FILTER(key_p, low, hi);
#if RETURN_FILTER == 1
        filt[gid] = filt_p;
#endif
        if (filt_p) {
            private ulong ind = indices[gid]-1;
            dataout[ind] = data[gid];
            keysout[ind] = key_p;
        }
        if (gid + 1 == ndata) *ndataout = indices[gid];
    }
}

