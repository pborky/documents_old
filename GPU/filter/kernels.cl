#define BSIZE (get_local_size(0)*get_local_size(1)*get_local_size(2))
#define BCOUNT (get_num_groups(0)*get_num_groups(1)*get_num_groups(2))
#define LID (get_local_id(0) + (get_local_size(0)*get_local_id(1)) + (get_local_size(0)*get_local_size(1)*get_local_id(2)))
#define BID (get_group_id(0) + (get_num_groups(0)*get_group_id(1)) + (get_num_groups(0)*get_num_groups(1)*get_group_id(2)))
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
    bsize = BSIZE;
    lid = LID;
    gid = GID;
    
    local ulong psum_l [LSIZE];
    private ulong psum_p;
    
    if (gid < ndata) {
        private KEYS_T key_p = keys[gid];
        psum_l[lid] = psum_p = FILTER(key_p, low, hi) ? 1:0;
    } else {
        psum_l[lid] = psum_p = 0;
    }
    
    for ( size_t i = 1; i < bsize ; i <<= 1 ) {
        barrier(CLK_LOCAL_MEM_FENCE);
        if (lid >= i) {
            psum_p += psum_l[lid-i];
        }
        if (i >= bsize>>1) break;
        barrier(CLK_LOCAL_MEM_FENCE);
        if (lid >= i) {
            psum_l[lid] = psum_p;
        }
    }
    
    if (gid < ndata)    psum[gid] = psum_p;
    if (lid+1 == bsize) bsum[BID] = psum_p;
    if (gid == 0)       *nbsum = BCOUNT;
}

kernel void prefixSumDownInplace (
    global ulong *          data,
    const ulong             ndata,
    global ulong *          psum,
    global ulong *          npsum
) {
    private ulong bsize, lid, gid;
    bsize = BSIZE;
    lid = LID;
    gid = GID;
    
    local ulong psum_l [LSIZE];
    private ulong psum_p;
    
    psum_l[lid] = psum_p = (gid < ndata) ? data[gid] : 0;
    
    for ( size_t i = 1; i < bsize ; i <<= 1 ) {
        barrier(CLK_LOCAL_MEM_FENCE);
        if (lid >= i) {
            psum_p += psum_l[lid-i];
        }
        if (i >= bsize>>1) break;
        barrier(CLK_LOCAL_MEM_FENCE);
        if (lid >= i) {
            psum_l[lid] = psum_p;
        }
    }
    
    if (gid < ndata)    data[gid] = psum_p;
    if (lid+1 == bsize) psum[BID] = psum_p;
    if (gid == 0)       *npsum = BCOUNT;
}

kernel void prefixSumUp (
    global ulong *              data,
    const ulong                 ndata,
    global ulong *              psum,
    const ulong                 npsum
) {
    private ulong bid, gid;
    bid = BID;
    gid = GID + BSIZE;
    
    local ulong psum_l;
    if (LID == 0) {
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
    
    if (gid < ndata) {
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

