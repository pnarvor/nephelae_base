import copy

class DeepcopyGuard:

    """
    Deepcopy guard

    This is an object intended to hide some object attributes from being
    deepcopied.  It is primarily used in nephelae.mapping.GprKernels because of
    cloning function of sklearn preventing deepcopy overrides and offering no
    satisfying solution for having a shallow copy.
    """

    def __init__(self, **parameters):

        self.parameters = parameters
        for key in parameters.keys():
            setattr(self, key, parameters[key])


    def __copy__(self, memo=None):
        
        # Check which line is better between the two below
        return DeepcopyGuard(**self.parameters)
        # return self


    def __deepcopy__(self, memo=None):
        """
        Returning a shallow copy of self since it is the purpose of this
        object.
        """
        return self.__copy__(self)



