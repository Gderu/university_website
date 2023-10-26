import functools


def login_required(view):
    @functools.wraps(view)
    def wrapped_view1(**kwargs):
        return view(**kwargs)

    return wrapped_view1


def admin_required(view):
    @login_required
    @functools.wraps(view)
    def wrapped_view2(**kwargs):
        return view(**kwargs)

    return wrapped_view2


def foo():
    print("Hi")


admin_required()(foo)()