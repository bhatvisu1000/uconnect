def myConnection(extra_value=None):
    print "Arguments to decorator", extra_value
    def _my_decorator(view_func):
        print "In _my_decorator"
        def _decorator(request, *args, **kwargs):
            print "In _decorator"
            # maybe do something before the view_func call
            # that uses `extra_value` and the `request` object
            response = view_func(request, *args, **kwargs)
            print "response", response
            # maybe do something after the view_func call
            return response
        return view_func(_decorator)
    return _my_decorator

# how to use it...
#def foo(request): 
#    print("HttpResponse('...')")
#
#foo = my_decorator('some-custom-value')(foo)

# or...
@myConnection('some-custom-value')
def foo(request):
   print "HttpResponse('...')", request

#foo('Print value')