from rx import Observable, Observer
from rx.anonymousobservable import AnonymousObservable
from rx.disposables import CompositeDisposable
from rx.internal import extensionclassmethod

@extensionclassmethod(Observable)
def when(cls, *args):
    """Joins together the results from several patterns.

    :param [Plan] args: A series of plans (specified as a list of as a series
        of arguments) created by use of the Then operator on patterns.
    :returns: Observable sequence with the results form matching several
        patterns.
    :rtype: Observable
    """

    plans = args[0] if len(args) and isinstance(args[0], list) else args
    print(plans)
    print(args)

    def subscribe(observer):
        active_plans = []
        external_subscriptions = {}

        def on_error(err):
            print(err)
            for v in external_subscriptions:
                v.on_error(err)
            observer.on_error(err)

        out_observer = Observer(observer.on_next, on_error, observer.on_completed)

        def func(active_plan):
            active_plans.remove(active_plan)
            if not len(active_plans):
                observer.on_completed()
        try:
            for plan in plans:
                active_plans.append(plan.activate(external_subscriptions, out_observer, func))

        except Exception as e:
            print(e)
            Observable.throw(e).subscribe(observer)

        group = CompositeDisposable()
        for join_observer in external_subscriptions:
            join_observer.subscribe()
            group.add(join_observer)

        return group

    return AnonymousObservable(subscribe)