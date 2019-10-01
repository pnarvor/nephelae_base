import threading

class ObserverSubject:

    """
    ObserverSubject

    Basic implementation of the observer pattern. Store a list of observer
    objects to be notified when a change occurs in the ObserverSubject.
    (more on this design pattern here : https://en.wikipedia.org/wiki/Observer_pattern)

    This is a generic class to be subclassed for a specific purpose.
    (Used as a mother class.)

    An example of implementation in this project is the notification sent to
    the GUI by the UAV objects listening to Paparazzi updates.
    (See nephelae_gui/consumers.py for more details).

    Attributes
    ----------

    notifyMethodName : str
        The name of the method to be called when notifyind an object.

    observerCallbacks : dict
        Dictionary of methods to be called on notification. Keys are observer
        objects ids and value are their notification callback methods.

    lock : threading.Lock
        A mutex for thread safety (mostly for preventing notifications
        happening at the same time as the insertion of a new observer).


    Methods
    -------

    check_notifiable(object) -> bool:
        Check if the object is notifiable (i.e. if it contains a method with
        the same name contained in self.notificationMethodName). If True,
        the object is suitable to be added as an observer.

    attach_observer(observer) -> None:
        Effectively insert an object in the observer list.
        Raise an exception if the object is not notifiable.

    do_notify(*args, **kwargs) -> None:
        Iterates through self.observers and calls each callback.
        TODO : check if should happen in a separated thread and use a callback
        queue (probably yes).

    {notifyMethodName}(*args, **kwargs) -> None:
        Alias for self.do_notify(). Is Dynamically created at object
        initialization.
        For exemple : if self.notifyMethodName == 'notify_this', then the 
        ObserverSubject instance has a new method called
        self.notify_this(*args, **kwargs) which simply calls
        self.do_notify(args, kwargs).

    """

    def __init__(self, notifyMethodName='notify'):

        """
        Parameters
        ----------
        notifyMethodName : str
            The name of the method to be called when notifyind an object.
            A new method called this name will be created for this object.
            For exemple : if self.notifyMethodName == 'notify_this', then the
            ObserverSubject instance has a new method called
            self.notify_this(*args, **kwargs) which simply calls
            self.do_notify(args, kwargs).
        """

        self.notifyMethodName = notifyMethodName
        self.observers = {}
        setattr(self, notifyMethodName,
                lambda *args, **kwargs: self.do_notify(*args, **kwargs))
        self.lock = threading.Lock()
 

    def check_notifiable(self, other):
        """Checks if an object is notifiable
        
        i.e. checks if an object  contains a method called self.{notifyMethodName}

        Parameters
        ----------
        other : object
            Object to be checked

        Returns
        -------
        boolean
            True if other is notifiable.
        """

        notifyMethod = getattr(other, self.notifyMethodName, None)
        if not callable(notifyMethod):
            return False
        else:
            return True
 

    def attach_observer(self, observer):

        """Add an observer

        Parameters
        ----------
        observer : object
            Observer object to be subscribed to self.

        Raises
        ------
        AttributeError
            If observer is not notifiable.
        """

        with self.lock:
            if not self.check_notifiable(observer):
                raise AttributeError("Observer is not '" + self.notifyMethodName +
                                     "' notifiable")
            self.observers[id(observer)] = getattr(observer,
                                                           self.notifyMethodName)


    def detach_observer(self, observer):

        """Remove an observer

        Parameters
        ----------
        observer : object
            Observer object to be removed from self.

        Raises
        ------
        KeyError
            If observer is not in self.observers.
        """

        with self.lock:
            try:
                del self.observers[id(observer)]
            except KeyError as e:
                raise KeyError("Observer not found :", e)


    def do_notify(self, *args, **kwargs):

        """Effectively calls callback method of all observers

        Parameters:
        -----------
        *args,**kwargs : any types
            Any number of arguments. Python will raise a TypeError exception
            if these arguments do not match the observers callback methods
            signature.
        """

        with self.lock:
            for callback in self.observers.values():
                callback(*args, **kwargs)
            

class MultiObserverSubject:
    
    """
    MultiObserverSubject

    ObserverSubject with multiple distinct notification methods.
    Works essentially the same way as ObserverSubject.

    The rational is to be able to notify different objects for different types
    of updates.

    Attributes
    ----------

    observerSubjects : dict(ObserverSubject)
        Dictionary of ObserverSubject instances to be able to handle several
        notification methods, so several list of observers.
    """

    def __init__(self, notificationMethods=[]):

        self.observerSubjects = {}
        self.lock = threading.Lock()
        for notifMethod in notificationMethods:
            self.add_notification_method(notifMethod)


    def add_notification_method(self, notifMethod):

        with self.lock:
            if notifMethod in self.observerSubjects.keys():
                return
            self.observerSubjects[notifMethod] = ObserverSubject(notifMethod)
            setattr(self, notifMethod,
                    lambda *args,**kwargs: self.observerSubjects[notifMethod].do_notify(*args,**kwargs))


    def attach_observer(self, observer, notifMethodName='notify'):

        if isinstance(notifMethodName, str):
            with self.lock:
                if notifMethodName not in self.observerSubjects.keys():
                    raise KeyError("'" + notifMethodName + "' is not a notifiable method")
                self.observerSubjects[notifMethodName].attach_observer(observer)
        elif isinstance(notifMethodName, list):
            for notifMethod in notifMethodName:
                self.attach_observer(observer, notifMethod)
        else:
            raise ValueError("notifMethodName must either a string or " +
                             "a list of strings.")


    def detach_observer(self, observer, notifMethodName=None):

        if isinstance(notifMethodName, str):
            with self.lock:
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

