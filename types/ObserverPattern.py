

class ObserverSubject:

    """ObserverSet

    Generic class to handle observer pattern.

    Store notification callbacks in a object id keyed dict.

    """

    def __init__(self, notifyMethodName='notify'):

        self.notifyMethodName = notifyMethodName
        self.observerCallbacks = {}
        setattr(self, notifyMethodName,
                lambda *args, **kwargs: self.notify(*args, **kwargs))
 

    def check_notifiable(self, other):

        notifyMethod = getattr(other, self.notifyMethodName, None)
        if not callable(notifyMethod):
            return False
        else:
            return True
 

    def attach_observer(self, observer):

        if not self.check_notifiable(observer):
            raise AttributeError("Observer is not '" + self.notifyMethodName +
                                 "' notifiable")
        self.observerCallbacks[id(observer)] = getattr(observer,
                                                       self.notifyMethodName)


    def detach_observer(self, observer):

        try:
            del self.observerCallbacks[id(observer)]
        except KeyError as e:
            raise KeyError("Observer not found :", e)


    def notify(self, *args, **kwargs):

        for callback in self.observerCallbacks.values():
            callback(*args, **kwargs)
            

class MultiObserverSubject:
    
    """ObserverMultiSet

    Helper class to handle several observer types at once.

    """

    def __init__(self, notificationMethods=[]):

        self.observerSubjects = {}
        for notifMethod in notificationMethods:
            self.add_notification_method(notifMethod)


    def add_notification_method(self, notifMethod):

        if notifMethod in self.observerSubjects.keys():
            return
        self.observerSubjects[notifMethod] = ObserverSubject(notifMethod)
        setattr(self, notifMethod,
                lambda *args,**kwargs: self.observerSubjects[notifMethod].notify(*args,**kwargs))


    def attach_observer(self, observer, notifMethodName='notify'):

        if isinstance(notifMethodName, str):
            self.observerSubjects[notifMethodName].attach_observer(observer)
        elif isinstance(notifMethodName, list):
            for notifMethod in notifMethodName:
                self.attach_observer(observer, notifMethod)
        else:
            raise ValueError("notifMethodName must either a string or " +
                             "a list of strings.")


    def detach_observer(self, observer, notifMethodName=None):

        if isinstance(notifMethodName, str):
            self.observerSubjects[notifMethodName].detach_observer(observer)
        elif isinstance(notifMethodName, list):
            for notifMethod in notifMethodName:
                self.detach_observer(observer, notifMethod)
        elif notifMethodName is None:
            for subject in self.observerSubjects.values():
                try:
                    subject.detach_observer(observer)
                except KeyError as e:
                    continue
        else:
            raise ValueError("notifMethodName must either a string or " +
                             "a list of strings.")

