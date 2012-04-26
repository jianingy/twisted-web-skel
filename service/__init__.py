from twisted.web import resource
from infrastructure import debug
from twisted.python.failure import Failure
from twisted.web.server import NOT_DONE_YET
from ujson import encode as json_encode
import time

__all__ = ["site_root", "BasePage"]

site_root = resource.Resource()


class ServiceError(Exception):

    code = 500
    message = "500 Internal Server Error"


class BasePage(resource.Resource):

    isLeaf = True

    def cancel(self, error, call):
        debug("Cancelling request: %s" % repr(error))
        call.cancel()

    def render(self, *args, **kwargs):
        self.__startTime__ = time.time()
        return resource.Resource.render(self, *args, **kwargs)

    def finish(self, value, request):
        if isinstance(value, Failure):
            error = value.value
            if isinstance(error, ServiceError):
                request.setResponseCode(error.code)
                message = error.message
                if isinstance(message, dict):
                    message["traceback"] = value.getTraceback()
                elif isinstance(message, str):
                    message += value.getTraceback()
            else:
                request.setHeader("Content-Type", "text/plain; charset=UTF-8")
                request.setResponseCode(500)
                message = "500 Internal Server Error: UNKNOWN\n"
                message += value.getTraceback()
        else:
            message = value

        if isinstance(message, dict):
            request.write(json_encode(message))
        elif isinstance(message, str):
            request.write(message)
        else:
            request.setResponseCode(500)
            request.write("500 Internal Server Error: Invalid Content Type")

        request.finish()

        debug("response latency: %.3fms" % \
              (time.time() - self.__startTime__) * 1000)

    def render_GET(self, request):
        if not hasattr(self, "async_GET"):
            return "Method Not Allowed"
        d = self.async_GET(request)
        request.notifyFinish().addErrback(self.cancel, d)
        d.addBoth(self.finish, request)
        return NOT_DONE_YET

    def render_POST(self, request):
        if not hasattr(self, "async_POST"):
            return "Method Not Allowed"
        d = self.async_POST(request)
        request.notifyFinish().addErrback(self.cancel, d)
        d.addBoth(self.finish, request)
        return NOT_DONE_YET

    def render_PUT(self, request):
        if not hasattr(self, "async_PUT"):
            return "Method Not Allowed"
        d = self.async_PUT(request)
        request.notifyFinish().addErrback(self.cancel, d)
        d.addBoth(self.finish, request)
        return NOT_DONE_YET

    def render_DELETE(self, request):
        if not hasattr(self, "async_DELETE"):
            return "Method Not Allowed"
        d = self.async_DELETE(request)
        request.notifyFinish().addErrback(self.cancel, d)
        d.addBoth(self.finish, request)
        return NOT_DONE_YET
