kernel void filterPrepare (
    global const %(TYPE_DATA)s  *data,
    global const %(TYPE_KEYS)s  *keys,
    const ulong                 ndata,
    const uint                  low,
    const uint                  high,
    global bool                 *filter,
    global ulong                *filtdata

) {    
    private size_t bsize = get_local_size(0)*get_local_size(1)*get_local_size(2);
    private size_t bcount = get_num_groups(0)*get_num_groups(1)*get_num_groups(2);
    
    private size_t lid = get_local_id(0) + get_local_size(0)*(get_local_id(1) + get_local_size(1)*get_local_id(2));
    private size_t bid = get_group_id(0) + get_num_groups(0)*(get_group_id(1) + get_num_groups(1)*get_group_id(2));
    private size_t gid = lid+bid*bsize;
    
    if (gid < ndata) {
        private %(TYPE_KEYS)s key_p = keys[gid];
        private bool filt_p = (key_p >= low) && (key_p < high);
        filter[gid] = filt_p;
        filtdata[gid] = filt_p;
    }
}
kernel void prefixSumDown (
    global ulong                *data,
    const ulong                 ndata,
    global ulong                *psum,
    global ulong                *npsum
) {
    private size_t bsize = get_local_size(0)*get_local_size(1)*get_local_size(2);
    private size_t bcount = get_num_groups(0)*get_num_groups(1)*get_num_groups(2);
    
    private size_t lid = get_local_id(0) + get_local_size(0)*(get_local_id(1) + get_local_size(1)*get_local_id(2));
    private size_t bid = get_group_id(0) + get_num_groups(0)*(get_group_id(1) + get_num_groups(1)*get_group_id(2));
    private size_t gid = lid + bid*bsize;
    
    local ulong psum_l [%(LOCAL_SIZE)d];
    
    private ulong psum_p = (gid < ndata) ? data[gid] : 0;

    for ( ulong i = 1; i < bsize ; i *= 2 ) {
        psum_l[lid] = psum_p;
        barrier(CLK_LOCAL_MEM_FENCE);
        if ((lid >= i) && (gid < ndata)) {
            psum_p += psum_l[lid-i];
        }
    }
    if (gid < ndata) {
        data[gid] = psum_p;
    }
    if (lid+1 == bsize) {
        psum[bid] = psum_p;
    }
    if (gid == 0) {
        *npsum = bcount;
    }
}
kernel void prefixSumUp (
    global ulong                *data,
    const ulong                 ndata,
    global ulong                *psum,
    const ulong                 npsum
) {
    private size_t bsize = get_local_size(0)*get_local_size(1)*get_local_size(2);
    private size_t bcount = get_num_groups(0)*get_num_groups(1)*get_num_groups(2);
    
    private size_t lid = get_local_id(0) + get_local_size(0)*(get_local_id(1) + get_local_size(1)*get_local_id(2));
    private size_t bid = get_group_id(0) + get_num_groups(0)*(get_group_id(1) + get_num_groups(1)*get_group_id(2));
    
    private size_t gid = lid + (bid+1)*bsize;
    
    local ulong psum_l;
    if ((bid < npsum) && (gid < ndata) && (lid == 0)) {
        psum_l = psum[bid];
    }
    barrier(CLK_LOCAL_MEM_FENCE);
    if ((bid < npsum) && (gid < ndata)) {
        private size_t psum_p = psum_l;
        data[gid] += psum_p;
    }
}
kernel void filter (
    global const %(TYPE_DATA)s  *data,
    global const %(TYPE_KEYS)s  *keys,
    global const bool           *filter,
    global const ulong          *indices,
    const ulong                 ndatain,
    global %(TYPE_DATA)s        *dataout,
    global %(TYPE_KEYS)s        *keysout,
    global ulong                *ndataout
) {
    private size_t bsize = get_local_size(0)*get_local_size(1)*get_local_size(2);
    private size_t bcount = get_num_groups(0)*get_num_groups(1)*get_num_groups(2);
    
    private size_t lid = get_local_id(0) + get_local_size(0)*(get_local_id(1) + get_local_size(1)*get_local_id(2));
    private size_t bid = get_group_id(0) + get_num_groups(0)*(get_group_id(1) + get_num_groups(1)*get_group_id(2));
    private size_t gid = lid+bid*bsize;
    
    if (gid < ndatain) {
        if (filter[gid]) {
            private ulong ind = indices[gid]-1;
            dataout[ind] = data[gid];
            keysout[ind] = keys[gid];
        }
        if (gid + 1 == ndatain) *ndataout = indices[gid];
    }
}


