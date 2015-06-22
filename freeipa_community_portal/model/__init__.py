from ipalib import api

api.bootstrap(context='cli')
api.finalize()
api.Backend.rpcclient.connect()
