from Ganga.Runtime.GPIexport                         import exportToGPI
from Ganga.GPIDev.Base.Proxy                         import addProxy, stripProxy
from Ganga.Utility.Config                            import getConfig
from Ganga.Utility.logging                           import getLogger
from GangaDirac.Lib.Server.WorkerThreadPool          import WorkerThreadPool
from GangaDirac.Lib.Utilities.ThreadPoolQueueMonitor import ThreadPoolQueueMonitor
logger = getLogger()
dirac_ganga_server      = WorkerThreadPool()
dirac_monitoring_server = WorkerThreadPool()
exportToGPI('queues',ThreadPoolQueueMonitor(),'Objects')

#\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/#
def diracAPI(cmd, timeout = 60):
    '''Execute DIRAC API commands from w/in Ganga.

    The stdout will be returned, e.g.:
    
    # this will simply return 87
    diracAPI(\'print 87\')
    
    # this will return the status of job 66
    # note a Dirac() object is already provided set up as \'dirac\'
    diracAPI(\'print Dirac().status([66])\')
    diracAPI(\'print dirac.status([66])\')

    # or can achieve the same using command defined and included from
    # getConfig('DIRAC')['DiracCommandFiles']
    diracAPI(\'status([66])\')

    '''
    return dirac_ganga_server.execute(cmd, timeout=timeout)

exportToGPI('diracAPI',diracAPI,'Functions')

#\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/#
def diracAPI_interactive(connection_attempts=5):
    '''
    '''
    import os, time,inspect,traceback
    from GangaDirac.Lib.Server.InspectionClient import runClient
    serverpath = os.path.join(os.path.dirname(inspect.getsourcefile(runClient)),'InspectionServer.py')
    dirac_ganga_server.execute_nonblocking("execfile('%s')"%serverpath, timeout=None, shell=False, priority = 1)
    
    time.sleep(1)
    print "\nType 'q' or 'Q' or 'exit' or 'exit()' to quit but NOT ctrl-D"
    i=0
    excpt = None
    while i < connection_attempts:
        try:
            runClient()
            break
        except:
            if i==(connection_attempts - 1):
                excpt=traceback.format_exc()
        finally:
            ++i
    return excpt
exportToGPI('diracAPI_interactive',diracAPI_interactive,'Functions')

#\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/#
def diracAPI_async(cmd, timeout = 120):
    '''Execute DIRAC API commands from w/in Ganga.
    '''
    return dirac_ganga_server.execute_nonblocking(cmd, timeout=timeout, priority = 2)

exportToGPI('diracAPI_async',diracAPI_async,'Functions')

#\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/#
def getDiracFiles():
    import os
    from Ganga.GPI import DiracFile
    from Ganga.GPIDev.Lib.GangaList.GangaList import GangaList
    filename = getConfig('DIRAC')['DiracLFNBase'].replace('/','-') + '.lfns'
    logger.info('Creating list, this can take a while if you have a large number of SE files, please wait...')
    dirac_ganga_server.execute('dirac-dms-user-lfns &> /dev/null', shell=True, timeout=None)
    g=GangaList()
    with open(filename[1:],'r') as lfnlist:
        lfnlist.seek(0)
        g.extend((DiracFile(lfn='%s'% lfn.strip()) for lfn in lfnlist.readlines()))
    return addProxy(g)
 
exportToGPI('getDiracFiles',getDiracFiles,'Functions')

#\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/#
def dumpObject(object, filename):
    import pickle
    f=open(filename, 'wb')
    pickle.dump(stripProxy(object), f)
    f.close()
exportToGPI('dumpObject',dumpObject,'Functions')

def loadObject(filename):
    import pickle
    f=open(filename, 'rb')
    r = pickle.load(f)
    f.close()
    return addProxy(r)
exportToGPI('loadObject',loadObject,'Functions')

#\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/#