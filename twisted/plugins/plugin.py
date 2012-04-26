from zope.interface import implements
from twisted.python import usage
from twisted.plugin import IPlugin
from twisted.application.service import IServiceMaker


class Options(usage.Options):
    optParameters = [
        ["config", "c", "conf/development.yaml", "Path to configuration"]
    ]


class ServiceMaker(object):
    implements(IServiceMaker, IPlugin)

    tapname = "twisted-web-skel"
    description = "a twisted web server skeleton"
    options = Options

    def makeService(self, options):

        from infrastructure import configure, build_server
        from service import site_root
        configure(options["config"])

        return build_server(site_root)

serviceMaker = ServiceMaker()
