# This file declares all classes which can be instanciated. The classes types
# are stored in string keyed dictionaries defining the mapping between strings
# and types. This is done to avoid an unsafe yaml load or the use of the eval
# python function which have security issues.

# TODO smart import procedure
from nephelae.mapping import NephKernel, WindKernel

kernels = {'NephKernel': NephKernel,
           'WindKernel': WindKernel}




