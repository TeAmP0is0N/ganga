################################################################################
# Ganga Project. http://cern.ch/ganga
#
# $Id: CopySplitter.py,v 1.1 2008-07-17 16:41:12 moscicki Exp $
################################################################################
from Ganga.GPIDev.Adapters.ISplitter import ISplitter
from Ganga.GPIDev.Schema import Schema,SimpleItem,Version

# a list of functions that can be called with the function_hook

def makeFirstSubJobFailExecutable(job,index):
    if index == 0:
        job.application.exe += 'foo'

class CopySplitter(ISplitter):
    """A simple splitter for testing. Does nothing at all clever"""
    _category = 'splitters'
    _name = 'CopySplitter'
    _schema = Schema(Version(1,0),{
        'number' : SimpleItem(defvalue=5),
        'function_hook': SimpleItem(defvalue=None,doc='Name of function in global namespace to call')
        })
            
    def split(self,job):

        subjobs=[]
        for i in range(self.number):
            j = self.createSubjob(job)

            j.splitter = None

            j.application = job.application
            j.backend = job.backend

            j.inputsandbox = job.inputsandbox[:]
            j.outputfiles = job.outputfiles[:]

            #gives tests a chance to alter subjobs
            if self.function_hook:
                g = globals()
                if g.has_key(self.function_hook):
                    g[self.function_hook](j,i)
            
            subjobs.append(j)
        return subjobs

#register with ganga
#from Ganga.Utility.Plugin import allPlugins
#allPlugins.add(CopySplitter,'splitters','CopySplitter')