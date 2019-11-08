# MethodType  allows to bound a function to an object and make it a method
from types import MethodType

class MethodCompound:
    """
    method_compound

    Proxy function for calling two fonctions in one call.  Returned values are
    appended into a list. If one of the callee is a method_compound, the output
    of the callee is assumed a list and results of the other callee are
    appended.

    To be used with the 'append' and 'prepend' conflict modes when loading a
    plugin.
    """
    
    def __init__(self, methods):
        for method in methods:
            if not callable(method):
                raise ValueError(str(method) + " is not callable !")
        self.methods = methods

    def __call__(self, *args, **kwargs):
        res = []
        for method in self.methods:
            if isinstance(method, MethodCompound):
                res = res + method(*args, **kwargs)
            else:
                res.append(method(*args, **kwargs))
        return res




class Pluginable:

    """
    Pluginable

    This is a metaprogrammaming class intended to safely manage the addition of
    new methods and attributes to classes derived from this class. Can be
    viewed as an implementation of the Strategy pattern.


    Methods
    -------
    load_plugin(plugin, *args, **kwargs) :
        Will bound the methods returned by plugin.__pluginmethods__() to self
        and then call plugin.__initplugin__(self, *args, **kwargs) on self.
    """


    def load_plugin(self, plugin, *args, **kwargs):
        """
        load_plugin

        Will bound the methods returned by plugin.__pluginmethods__() to self
        and then call plugin.__initplugin__(self, *args, **kwargs) on self.

        When designing a plugin, each element returned by
        plugin.__pluginmethods__() should be a dictionary with the following
        elements:
        'method': function
            Reference to actual function to bind to self.
        'name':str
            Name of the function which will be used to call bound method.
            (Does not have to be the name as the original method name).
        'conflictMode' : either 'append', 'prepend', 'replace' or 'abort'
            This specifies the behavior if self has already a method called
            'name' then trying to bind a new method.
            'append'  : old method will be called first, then the new one.
            'prepend' : new method will be called first, then the old one.
            'replace' : new method replaces old method
            'abort'   : abort binding without error
            Using any other value will raise an exception, but only if there
            is a conflict.

        Parameters
        ----------
        plugin : class
            plugin class to be applyed to self
            /!\ No instance of this class will be created. Instead the methods
            will be added to this object, and a __initplugin__ method will
            be called. The __initplugin__ method may add or modify arguments
            in this object.
            Must also define a __pluginmethods__ getter returning the method to
            add to this object.

        args, kwargs :
            Arguments to be passed down to plugin.__initplugin__
        """

        for method in plugin.__pluginmethods__():
            # Building new method with respect to the insertMode
            if hasattr(self, method['name']):

                if method['conflictMode'] == 'append':
                    setattr(self, method['name'], 
                            MethodCompound([getattr(self, method['name']),
                                           MethodType(method['method'], self)]))

                elif method['conflictMode'] == 'prepend':
                    setattr(self, method['name'], 
                            MethodCompound([MethodType(method['method'], self),
                                           getattr(self, method['name'])]))

                elif method['conflictMode'] == 'replace':
                    setattr(self, method['name'], 
                            MethodType(method['method'], self))

                elif method['conflictMode'] == 'abort':
                    pass

                else:
                    raise ValueError("Invalid conflictMode")

            else:
                setattr(self, method['name'],
                        MethodType(method['method'], self))
        
        # Initializing the plugin on this object with args and kwargs parameters
        plugin.__initplugin__(self,  *args, **kwargs)




















