execfile('{{ __extraction_folder }}/wsadminlib/bin/wsadminlib.py')

appList=listApplications()
appServers=listServersInCluster("Util")

if 'TinyEditorsServices' not in appList:
    installApplication('{{ __extraction_folder }}/TinyEditorsForConnections/services/editorsServices_c6.ear', appServers, 'Util' )

    AdminApp.install('{{ __extraction_folder }}/TinyEditorsForConnections/services/editorsServices_c6.ear', '[  -nopreCompileJSPs -distributeApp -nouseMetaDataFromBinary -nodeployejb -appname TinyEditorsServices -createMBeansForResources -noreloadEnabled -nodeployws -validateinstall warn -processEmbeddedConfig -filepermission .*\.dll=755#.*\.so=755#.*\.a=755#.*\.sl=755 -noallowDispatchRemoteInclude -noallowServiceRemoteInclude -asyncRequestDispatchType DISABLED -nouseAutoLink -noenableClientModule -clientMode isolated -novalidateSchema -MapModulesToServers [[ tiny-spelling.war tiny-spelling.war,WEB-INF/web.xml WebSphere:cell=ConnectionsCell,cluster=Util+WebSphere:cell=ConnectionsCell,node=cnx8cr6-db2-was-node,server=cnx8cr6-db2-was ][ tiny-hyperlinking.war tiny-hyperlinking.war,WEB-INF/web.xml WebSphere:cell=ConnectionsCell,cluster=Util+WebSphere:cell=ConnectionsCell,node=cnx8cr6-db2-was-node,server=cnx8cr6-db2-was ]] -MapWebModToVH [[ tiny-spelling.war tiny-spelling.war,WEB-INF/web.xml default_host ][ tiny-hyperlinking.war tiny-hyperlinking.war,WEB-INF/web.xml default_host ]]]' )

AdminApp.save()
