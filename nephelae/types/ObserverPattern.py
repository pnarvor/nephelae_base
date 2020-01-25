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

    observerCallbacks : dict({int:function})
        Dictionary of methods to be called on notification. Keys are observer
        objects ids (got if python id() function) and values are their
        notification callback methods.

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
        For example : if self.notifyMethodName == 'notify_this', then the 
        ObserverSubject instance has a new method called
        self.notify_this(*args, **kwargs) which simply calls
        self.do_notify(args, kwargs).

    """

    def __init__(self, notifyMethodName='notify'):

        """
        Parameters
        ----------
        notifyMethodName : str
            The name of the method to be called when notifying an object.
            A new method called this name will be created for this object.
            For exemple : if self.notifyMethodName == 'notify_this', then the
            ObserverSubject instance has a new method called
            self.notify_this(*args, **kwargs) which simply calls
            self.do_notify(args, kwargs).
        """

        self.notifyMethodName = notifyMethodName
        self.observers = {}

        # TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO 
        # Check if commenting this did not break anything (and propagate to
        # Multioberserver subject (it will break for MUltiobserver subject))
        # setattr(self, notifyMethodName,
        #         lambda *args, **kwargs: self.do_notify(*args, **kwargs))
        # TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO 

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
    observerSubjects : dict({str:ObserverSubject})
        Dictionary of ObserverSubject instances to be able to handle several
        notification methods, so several list of observers.

    lock : threading.Lock
        A mutex for thread safety (mostly for preventing notifications
        happening at the same time as the insertion of a new notification method).


    Methods
    -------
    add_notification_method(notifMethodName) -> None:
        Creates a new notification method. Will do nothing if notifMethodName
        already in self.observerSubjects.keys().

    attach_observer(observer, notifMethodName) -> None:
        Subscribes an observer to notifMethodName. notifMethodName can be a list
        of notification method name. In this case the observer will be
        subscribed to all these methods.
        
    detach_observer(observer, notifMethodName) -> None:
        Removes an observer. If notifMethodName is None, the observer will be
        removed from all ObserverSubjects. notifMethodName can also be a list
        of names.
    """

    def __init__(self, notificationMethods=[]):

        """
        Parameters
        ----------
        notificationMethods : list(str)
            list of nofication method names to be handled.
            A new alias method for this instance will be created with each of
            these names. See ObserverSubject.__init__() for details.
        """

        self.observerSubjects = {}
        self.lock = threading.Lock()
        for notifMethod in notificationMethods:
            self.add_notification_method(notifMethod)


    def add_notification_method(self, notifMethod):
        """
        Creates a new callable notification method, by creating a new
        ObserverSubject instance in self.observerSubjects.

        Will also creates a notification alias self.{notifMethod}.
        See ObserverSubject.__init__() for details.

        If notifMethod already exists in self.observerSubjects.keys(), does nothing.

        Parameters
        ----------
        notifMethod : str
            Notification method name to be created.
        """

        with self.lock:
            if notifMethod in self.observerSubjects.keys():
                return
            self.observerSubjects[notifMethod] = ObserverSubject(notifMethod)
            setattr(self, notifMethod,
                    lambda *args,**kwargs: self.observerSubjects[notifMethod].do_notify(*args,**kwargs))


    def attach_observer(self, observer, notifMethodName='notify'):

        """Subscribe an observer to a notification method

        Can be subscribed to several notification methods if notifMethodName
        is a list of names.

        /!\ If notifMethodName is a list of str, this method is called on each
        element of the list. (Has a kind of recursion behavior).

        Parameters
        ----------
        observer : object
            Observer object to be subscribed.
        notifMethodName : str or list(str)
            Nofification method names to which the observer must subscribe.

        Raises
        ------
        AttributeError
            If observer is not notifiable.
        ValueError
            if notifMethodName is neither a str or a list of str.
        """

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

        """Remove an observer to a notification method

        Can be removed from several notification methods if notifMethodName
        is a list of names.

        /!\ If notifMethodName is a list of str, this method is called on each
        element of the list. (Has a kind of recursion behavior).

        Parameters
        ----------
        observer : object
            Observer object to be removed.
        notifMethodName : str or list(str)
            Nofification method names from which the observer must be removed.

        Raises
        ------
        ValueError
            if notifMethodName is neither a str or a list of str.
        """

        if isinstance(notifMethodName, str):
            with self.lock:
                self.observerSubjects[notifMethodName].detach_observer(observer)
        elif isinstance(notifMethodName, list):
            for notifMethod in notifMethodName:
                self.detach_observer(observer, notifMethod)
        elif notifMethodName is None:
            with self.lock:
                for subject in self.observerSubjects.values():
                    try:
                        subject.detach_observer(observer)
                    except KeyError as e:
                        # Is raised if the observer was not subscribed
                        # Seems ok to let this exception go because we try to
                        # unsubscribe it anyway.
                        print("Warning, observer not found while unsubscribing.")
                        print("Exception feedback :", e)
        else:
            raise ValueError("notifMethodName must either a string or " +
                             "a list of strings.")

