#define BSIZE (get_local_size(0)*get_local_size(1)*get_local_size(2))
#define BCOUNT (get_num_groups(0)*get_num_groups(1)*get_num_groups(2))
#define LID (get_local_id(0) + get_local_size(0)*(get_local_id(1) + get_local_size(1)*get_local_id(2)))
#define BID (get_group_id(0) + get_num_groups(0)*(get_group_id(1) + get_num_groups(1)*get_group_id(2)))
#define GID (LID + (BID * BSIZE))

#define DATA_T %(TYPE_DATA)s
#define KEYS_T %(TYPE_KEYS)s
#define LSIZE %(LOCAL_SIZE)d

kernel void filterPrepare (
    global const DATA_T     *data,
    global const KEYS_T     *keys,
    const ulong             ndata,
    const KEYS_T            low,
    const KEYS_T            high,
    global bool             *filter
) {
    private size_t gid = GID;
    
    if (gid < ndata) {
        private KEYS_T key_p = keys[gid];
        private bool filt_p = ((key_p >= low) && (key_p < high)) ? 1:0;
        filter[gid] = filt_p;
    }
}

kernel void prefixSumDown (
    global const bool       *dataB,
    global ulong            *data,
    const ulong             ndata,
    global ulong            *psum,
    global ulong            *npsum
) {
    private size_t bsize, lid, gid;
    bsize = BSIZE;
    lid = LID;
    gid = GID;

    local ulong psum_l [LSIZE];

    private ulong psum_p = ((gid < ndata) && dataB[gid]) ? 1 : 0;
    
    for ( ulong i = 1; i < bsize ; i <<= 1 ) {
        psum_l[lid] = psum_p;
        barrier(CLK_LOCAL_MEM_FENCE);
        if (lid >= i) {
            psum_p += psum_l[lid-i];
        }
    }
        
    if (gid < ndata)    data[gid] = psum_p;
    if (lid+1 == bsize) psum[BID] = psum_p;
    if (gid == 0)       *npsum = BCOUNT;
}

kernel void prefixSumDownInplace (
    global ulong                *data,
    const ulong                 ndata,
    global ulong                *psum,
    global ulong                *npsum
) {
    private size_t bsize, lid, gid;
    bsize = BSIZE;
    lid = LID;
    gid = GID;
    
    local ulong psum_l [LSIZE];
    
    private ulong psum_p = (gid < ndata) ? data[gid] : 0;
    
    for ( ulong i = 1; i < bsize ; i <<= 1 ) {
        psum_l[lid] = psum_p;
        barrier(CLK_LOCAL_MEM_FENCE);
        if (lid >= i) {
            psum_p += psum_l[lid-i];
        }
    }
    
    if (gid < ndata)    data[gid] = psum_p;
    if (lid+1 == bsize) psum[BID] = psum_p;
    if (gid == 0)       *npsum = BCOUNT;
}

kernel void prefixSumUp (
    global ulong                *data,
    const ulong                 ndata,
    global ulong                *psum,
    const ulong                 npsum
) {
    private size_t bid, gid;
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
    global const DATA_T     *data,
    global const KEYS_T     *keys,
    global const bool       *filter,
    global const ulong      *indices,
    const ulong             ndatain,
    global DATA_T           *dataout,
    global KEYS_T           *keysout,
    global ulong            *ndataout
) {
    private size_t gid = GID;
    
    if (gid < ndatain) {
        if (filter[gid]) {
            private ulong ind = indices[gid]-1;
            dataout[ind] = data[gid];
            keysout[ind] = keys[gid];
        }
        if (gid + 1 == ndatain) *ndataout = indices[gid];
    }
}

