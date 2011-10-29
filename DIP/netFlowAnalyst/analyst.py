import logging
logger = logging.getLogger()

class Main(object):
    FLOWS_FILE = 'flows.h5'
    FILTER_FILE = 'filters.json'
    BIN_WIDTH = 1000
    def __init__(self, argv, flowsFile=FLOWS_FILE, filterFile=FILTER_FILE, binWidth = BIN_WIDTH):
        self.flowsFile = flowsFile
        self.filterFile = filterFile
        self.binWidth = binWidth
        self.filtering = None
        self.filterData = None
        self.bins = None
        logger.debug('args: '+ str(argv))
        for i in range(1,len(argv),2):
            if argv[i] == 'binWidth':
                self.binWidth = int(argv[i+1])
            if argv[i] == 'flowsFile':
                self.flowsFile = argv[i+1]
            if argv[i] == 'filterFile':
                self.filterFile = argv[i+1]
        logger.info('binWidth = %d' % self.binWidth)
        logger.info('flowsFile = %s' % self.flowsFile)
        logger.info('filterFile = %s' % self.filterFile)

    
    def load(self):
        import json
        import io
        import h5py
        from numpy import array
        
        file1 = h5py.File(self.flowsFile)
        file2 = io.open(self.filterFile)
        try:
            self.filters = None
            self.filterData = None

            flows = file1['flows']            
            if 'bins' in flows.keys():
                logger.info('Loading bins..')
                self.bins = flows['bins']['data'][:]
                logger.info('Loading filters..')
                self.filterData = dict((k,flows['filters'][k][:]) for k in flows['filters'].keys())
            else:
                logger.info('Loading data..')
                self.ipmap = flows['ipmap'][:]
                self.protocols = dict([(k,flows['PROTOCOLS'][k].value) for k in flows['PROTOCOLS'].keys()])
                self.data = flows['data'][:]
                logger.info('Still loading data..')
                self.dataLong = flows['dataLong'][:]
                self.dataFields = dict([(k,flows['FIELDS'][k].value) for k in flows['FIELDS'].keys()])
                self.dataFieldsLong = dict([(k,flows['FIELDS_LONG'][k].value) for k in flows['FIELDS_LONG'].keys()])
                if 'filtering' in flows.keys():
                    logger.info('Loading filters..')
                    self.filtering = flows['filtering'][:]
                    self.filters = flows['filters'][:]
                    self.filterData = dict((k,flows['filters'][k][:]) for k in flows['filters'].keys())
             
            if self.filters is not None or self.filterData is not None: return
            
            self.filters = json.load(file2)
            for k in range(len(self.filters)):
                
                for j in range(len(self.filters[k]['dstIPs'])):
                    if isinstance(self.filters[k]['dstIPs'][j], basestring): 
                        ip = [tuple(int(i) for i in self.filters[k]['dstIPs'][j].split('.')),]
                        ip = self.ipmap[(self.ipmap[:,1:]==ip).min(1),0]
                        if len(ip) == 0: ip = 0
                        else: ip = ip.item()
                        self.filters[k]['dstIPs'][j] = ip
                if len(self.filters[k]['dstIPs'])  > 0:
                    self.filters[k]['dstIPs'] = [ i for i in self.filters[k]['dstIPs'] if i > 0 ]
                    if len(self.filters[k]['dstIPs']) == 0:
                        self.filters[k]['dstIPs'] = None
                
                for j in range(len(self.filters[k]['srcIPs'])):
                    if isinstance(self.filters[k]['srcIPs'][j], basestring): 
                        ip = [tuple(int(i) for i in self.filters[k]['srcIPs'][j].split('.')),]
                        ip = self.ipmap[(self.ipmap[:,1:]==ip).min(1),0]
                        if len(ip) == 0: ip = 0
                        else: ip = ip.item()
                        self.filters[k]['srcIPs'][j] = ip
                if len(self.filters[k]['srcIPs'])  > 0:
                    self.filters[k]['srcIPs'] = [ i for i in self.filters[k]['srcIPs'] if i > 0 ]
                    if len(self.filters[k]['srcIPs']) == 0:
                        self.filters[k]['srcIPs'] = None
                
                for j in range(len(self.filters[k]['protocols'])):
                    if isinstance(self.filters[k]['protocols'][j], basestring):
                        self.filters[k]['protocols'][j] = self.protocols[self.filters[k]['protocols'][j]]
            
            self.filters = [ f for f in self.filters if f['srcIPs'] is not None and f['dstIPs'] is not None ]
        finally:
            file1.close()
            file2.close()
    
    def doFiltering(self):
        if self.filtering is not None and self.filterData is not None: return
        
        from numpy import array,ndarray,logical_and
        self.filtering = ndarray(shape=(len(self.data), len(self.filters)),dtype=bool)
        self.filtering[:] = False
        logger.debug('Applying %d filters..' % len(self.filters))
        for f in range(len(self.filters)):
            results  = True
            for r in [
                       self.data[:,self.dataFields['SRC_IP']] == array([self.filters[f]['srcIPs'],]).transpose(),
                       self.data[:,self.dataFields['DST_IP']] == array([self.filters[f]['dstIPs'],]).transpose(),
                       self.data[:,self.dataFields['SRC_PORT']] == array([self.filters[f]['srcPorts'],]).transpose(),
                       self.data[:,self.dataFields['DST_PORT']] == array([self.filters[f]['dstPorts'],]).transpose(),
                       self.data[:,self.dataFields['PROT']] == array([self.filters[f]['protocols'],]).transpose()                      
                      ]: 
                if len(r) > 0: 
                    results &= r.max(0)
            self.filtering[results,f] = True
        return self.filtering
    
    def binrecurse(self, time, lowBounds, upBounds, data, filtering, timebounds, lvl):
        from numpy import ndarray,log,log2,power
        n = len(upBounds)
        # (t.min() - timebounds[0])/(timebounds[1]+ t.min() - t.max() )
        if n > 512: # divide and conquer
            b = upBounds[:(n/2)]
            m = b.max()
            i = time <= m
            t = time[i]
            logger.debug( '***%s progress = %d %%' % ('*'*lvl, 100*(t.min() - timebounds[0])/(timebounds[1] + t.min() - t.max() - timebounds[0] )))
            bins0 = self.binrecurse(t, lowBounds[:(n/2)], b, data[i,:], filtering[i,:],timebounds,lvl+1)
            
            b = lowBounds[(n/2):]
            m = b.min()
            i = time > m
            t = time[i]
            logger.debug( '***%s progress = %d %%' % ('*'*lvl, 100*(t.min() - timebounds[0])/(timebounds[1] + t.min() - t.max() - timebounds[0] )))
            bins1 = self.binrecurse(t, b, upBounds[(n/2):], data[i,:], filtering[i,:],timebounds,lvl+1)
            
            bins = ndarray(shape=(n,filtering.shape[1],2), dtype=float)
            bins[:(n/2),...] = bins0
            bins[(n/2):,...] = bins1
            return bins
        
        else:
            bins = ndarray(shape=(n,filtering.shape[1],2), dtype=float)
            logger.info('*** %d %% complete ' % (100*(time.min() - timebounds[0])/(timebounds[1] - timebounds[0] )))
            time.shape = (time.size,1)
            upBounds.shape = (1,upBounds.size)
            lowBounds.shape = (1,lowBounds.size)
            i = (time>lowBounds) & (time<=upBounds)
            logger.debug( '***%s indices shape %s' % ('*'*lvl, str(i.shape)))
            for bi in xrange(n):
                for fi in xrange(filtering.shape[1]):
                    ii = i[:,bi]
                    ii.squeeze()
                    ii = ii & filtering[:,fi]
                    b = data[ii,self.dataFields['BYTES']].sum()
                    p = data[ii,self.dataFields['PACKETS']].sum()
                    bins[bi,fi,0] = b/p
                    bins[bi,fi,1] = log(1+p)
            return bins
    
    def binning(self):
        if self.bins is not None: return
        from numpy import ndarray,array,log,log2,power
        time = self.dataLong[:,0]
        self.binsBounds = array(range(time.min(),time.max(),self.binWidth))
        n = int(power(2,int(log2(len(self.binsBounds))))) # ensure power-of-2
        self.binsBounds = self.binsBounds[:n+1]
        lowBounds = self.binsBounds[:-1]
        upBounds = self.binsBounds[1:]
        i = time<=upBounds.max()
        self.time = time = time[i]
        logger.debug( '** time = (%d, %d)' % (time.min(), time.max()))
        data = self.data[i,:]
        filtering = self.filtering[i,:]
        logger.debug('Binning..')
        self.bins = self.binrecurse(time, lowBounds, upBounds, data, filtering, (time.min(), time.max()),0)
        return self.bins
    
    def saveBins(self, name):
        import h5py
        f1 = h5py.File(name, 'w')
        try:
            flows = f1.create_group('flows')
            
            filters = flows.create_group('filters')
            filters.create_dataset('filterName', data = [ str(f['fileName']) for f in self.filters ] )
            filters.create_dataset('type', data = [ str(f['type']) for f in self.filters ] )
            filters.create_dataset('annotation', data = [ str(f['annotation']) for f in self.filters ] )
            
            bins = flows.create_group('bins')
            bins.create_dataset('lowBounds', data = self.binsBounds[:-1])
            bins.create_dataset('upBounds', data = self.binsBounds[1:])
            bins.create_dataset('bins', data = self.bins)
            bins.create_dataset('time', data = self.time)
        finally:
            f1.close()
    
    def spect(self, nfft = 8, overlap = 0, feature = 0):
        #specgram(main.bins[:,4,0], NFFT=128, noverlap=32)
        #[ (i, main.filterData['type'][i], int(main.bins[:,i,1].sum(0)), main.filterData['annotation'][i][:15], main.filterData['filterName'][i][:15]) for i in range(50) if main.bins[:,i,1].sum(0)>0 ]
    
        from matplotlib.pyplot import figure
        sel = (6,7,8,20,4,5,13,14,15)
        f = figure()
        a = [ f.add_subplot(len(sel),1,i) for i in range(len(sel)) ]
        for i in range(len(sel)):
            a[i].specgram(self.bins[:,sel[i],feature], NFFT=nfft, noverlap=overlap)
            a[i].set_title('%d: %s'%(sel[i],self.filterData['filterName'][sel[i]]))
        [ (i, self.filterData['type'][i], int(self.bins[:,i,feature].sum(0)), self.filterData['annotation'][i][:15], self.filterData['filterName'][i][:15]) for i in sel if self.bins[:,i,feature].sum(0)>0 ]
        f.show()
        return a
    
    def transform(self, data, wnd, overlap, wndfnc = None):
        from numpy import log2,exp2,floor,abs,tile
        from numpy.fft import fft
        nchan = data.shape[1]
        ndata = data.shape[0]/wnd
        ndim = wnd
        size = ndata*ndim
        data = data[:size,...].transpose()
        data.shape = (nchan, ndim, ndata)
        data = data.transpose()
        if wndfnc is not None:
            w = wndfnc(ndim)
            w.shape = (1,ndim,1)
            w = tile(w,(ndata,1,nchan))
            data = w*data
        return abs(fft(ndim*data,ndim,1))
    
    def plot(self, nfft = 8, overlap = 0, feature = 0):
        from numpy import hanning,tile
        from matplotlib.pyplot import figure
        sel = (6,7,8,20,4,5,13,14,15)
        data = self.bins[:,sel,feature]
        spect = self.transform(data, nfft, overlap, hanning)
        for i in range(len(sel)):
            f = figure()
            a = f.add_subplot(111)
            a.plot(spect[:,:,i].mean(1))
            a.plot(spect[:,:,i].var(1))
            a.legend([ self.filterData[i]['fileName'] for i in range(len(self.filterData)) if i in sel ])
            a.set_title('%d: %s'% (sel[i], self.filterData['filterName'][sel[i]]))
            f.show()
        
if __name__ == '__main__':
    import sys
    logging.basicConfig(stream = sys.stderr, level ='INFO', format='%(asctime)s [%(levelname)s] %(threadName)s: %(message)s')
    
    main = Main(sys.argv)

    from threading import Thread,currentThread
    class Scheduler(Thread):
        def __init__(self, name, actions):
            Thread.__init__(self,name=name)
            self.daemon = True
            self._actions = actions
        def run(self):
            logger.info( "*** Start. ***" )
            try:
                for do in self._actions:
                    if isinstance(do, list):
                        for doo in do:
                            doo.start()
                        for doo in do:
                            if doo.isAlive():
                                doo.join()
                    else:
                        do.start()
                        do.join()
            finally: logger.info( "*** Done. ***")
    class Do(Thread):
        def __init__(self, name, target):
            Thread.__init__(self,name=name)
            self.daemon = True
            self._target = target
        def run(self):
            logger.info( "*** Start. ***")
            try: self._target()
            finally: logger.info( "*** Done. ***")
    from numpy import log
    scheduler = Scheduler('SchedulerThread', [ 
                                  Do('LoadThread', main.load),
                                  Do('FilterThread', main.doFiltering),
                                  Do('BinnerThread0', main.binning), 
                                  Do('PloterThread0', main.plot) 
                              ])
    #scheduler.start()

