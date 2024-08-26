# Needs some work, maybe creating a list with heap sizes would be good.

class WasServers:

    def __init__(self):
        # Get a list of all servers in WAS cell (dmgr, nodeagents, AppServer,
        # webserver)
        self.AllServers = self.getAllServers()
        self.WebServers = self.getWebServers()
        self.AppServers = self.getAllServersWithoutWeb()
        # self.serverNum, self.jvm, self.cell, self.node, self.serverName = self.getAttrServers()
        self.serverNum, self.jvm, self.cell, self.node, self.serverName = self.getAttrServers()

    def getAllServers(self):
        # get a list of all servers
        self.servers = AdminTask.listServers().splitlines()
        return self.servers

    def getAppServers(self):
        # get a list of all application servers
        # includes webserver, but no dmgr and nodeagents
        self.servers = AdminTask.listServers(
            '[-serverType APPLICATION_SERVER]').splitlines()
        return self.servers

    def getWebServers(self):
        # get a list of all webservers
        self.webservers = AdminTask.listServers(
            '[-serverType WEB_SERVER]').splitlines()
        return self.webservers

    def getAllServersWithoutWeb(self):
        # inclusive dmgr and nodeagents
        self.AppServers = self.AllServers
        for webserver in self.WebServers:
            self.AppServers.remove(webserver)
        return self.AppServers

    def getAttrServers(self):
        # get jvm, node, cell from single application server
        srvNum = 0
        jvm = []
        cell = []
        node = []
        servername = []
        for server in self.AppServers:
            srvNum += 1
            javavm = AdminConfig.list('JavaVirtualMachine', server)
            jvm.append(javavm)
            srv = server.split('/')
            cell.append(srv[1])
            node.append(srv[3])
            servername.append(srv[5].split('|')[0])
        self.jvm = jvm
        cell = cell
        node = node
        servername = servername
        # return ( serverNum, jvm, cell, node, serverName )
        return (srvNum, self.jvm, cell, node, servername)

WS1 = WasServers()

for count in range(WS1.serverNum):
    jvm = WS1.jvm[count]
    cell = WS1.cell[count]
    node = WS1.node[count]
    servername = WS1.serverName[count]

    initialHeapSize = 3072
    maximumHeapSize = 3072

    if initialHeapSize == '':
        initialHeapSize = AdminConfig.showAttribute(jvm, 'initialHeapSize')

    if maximumHeapSize == '':
        maximumHeapSize = AdminConfig.showAttribute(jvm, 'maximumHeapSize')

    initialHeap = '[[ initialHeapSize ' + str(initialHeapSize) + ' ]]'
    maxHeap = '[[ maximumHeapSize ' + str(maximumHeapSize) + ' ]]'

    AdminConfig.modify(jvm, initialHeap)
    AdminConfig.modify(jvm, maxHeap)

if (AdminConfig.hasChanges()):
    print('Changed')
    AdminConfig.save()