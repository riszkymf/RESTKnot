from flask_restful import Resource, reqparse, request
from app.helpers.rest import *
from app.models import model as db
from app.helpers import cmd_parser as parse
from app.helpers import command as cmd
from app.libs import utils
# from app import sockets, BaseNamespace
import json, os
from app.middlewares.auth import login_required



# class CmdNamespace(BaseNamespace):
#     def initialize(self):
#         self.response = None

#     def on_response(self, *args):
#         list_data = list(args)
#         respons_sockets = list()
#         for i in list_data:
#             if i['data']['data'] == 'null':
#                 if i['data']['Description'] == '[]':
#                     data = {
#                         "command": i['data']['Description'],
#                         "error": True,
#                         "messages": "Block Type Command Not Parsing"
#                     }
#                 else:
#                     data = {
#                         "status": True,
#                         "messages": "Block Type Command Execute"
#                     }
#             else:
#                 data = {
#                     "status": i['data']['result'],
#                     "command": i['data']['Description'],
#                     "receive": json.loads(i['data']['data'])
#                 }
#             respons_sockets.append(data)
#         self.response = respons_sockets

class SendCommandRest(Resource):
    def get(self):
        pass
        # command = utils.get_command(request.path)
        # try:
        #     respons = db.result(command)
        # except Exception:
        #     respons = None
        # else:
        #     return response(200, data=respons)
    ##@jwt_required
    @login_required
    def post(self):
        url_env = os.getenv("SOCKET_AGENT_HOST")
        port = os.getenv("SOCKET_AGENT_PORT")
        url_fix= url_env+":"+port
        url = url_fix+"/api/command_rest"
        json_req = request.get_json(force=True)
        command = utils.get_command(request.path)
        init_data = parse.parser(json_req, command)
        respons = dict()
        
        if init_data['action'] == 'conf-read':
            respons = cmd.conf_read()
            http_respons = utils.send_http(url, data=respons)
            return response(200, data=http_respons)

        if init_data['action'] == 'conf-insert':
            tags = dict()
            for i in init_data['data']:
                tags = i['tags']
            respons = cmd.config_insert(tags)
            cmd.conf_begin_http(url)
            http_respons = utils.send_http(url,respons)
            cmd.conf_commit_http(url)
            return response(200, data=http_respons)

        if init_data['action'] == 'zone-read':
            tags = dict()
            for i in init_data['data']:
                tags = i['tags']
            respons = cmd.zone_read(tags)
            http_respons = utils.send_http(url, respons)
            return response(200, data=http_respons)

        if init_data['action'] == 'zone-soa-insert':
            result= list()
            for i in init_data['data']:
                tags = i['tags']
            print(" 1 ===> ",tags)
            begin_json = cmd.zone_begin(tags)
            print("2 ===> ", begin_json)
            begin_respon = utils.send_http(url,begin_json)
            print("3 ===>", begin_respon)
            result.append(begin_respon)

            try : 
                respons = cmd.zone_soa_insert_default(tags)
                print(" 4 ====> ", respons)
            except Exception as e :
                respons = {
                    "Status" : False,
                    "Error" : str(e)
                }
                return response(400, message = respons)
            else: 
                http_respons = utils.send_http(url,respons)
                result.append(http_respons)
                print(" 5 ===> ", http_respons)
                commit_json = cmd.zone_commit(tags)
                commit_response = utils.send_http(url,commit_json)
                print(" 6 ===> ", commit_response)
                result.append(commit_response)
                
                return response(200, data=result)

        if init_data['action'] == 'zone-begin':
            for i in init_data['data']:
                tags = i['tags']
            respons = cmd.zone_begin(tags)
            http_response = utils.send_http(url,respons)
            return response(200, data=http_response)

        if init_data['action'] == 'zone-commit':
            for i in init_data['data']:
                tags = i['tags']
            respons = cmd.zone_commit(tags)
            http_response = utils.send_http(url,respons)
            return response(200, data=http_response)

        if init_data['action'] == 'zone-insert':
            respons = list()
            for i in init_data['data']:
                tags = i['tags']
            json_begin = cmd.zone_begin_http(url,tags) 
            respons.append(json_begin)
            json_command = cmd.zone_insert(tags)
            http_response = utils.send_http(url,json_command)
            respons.append(http_response)
            res_commit = cmd.zone_commit_http(url,tags)
            respons.append(res_commit)
            return response(200, data=respons)

        if init_data['action'] == 'zone-ns-insert':
            respons = list()
            for i in init_data['data']:
                tags = i['tags']
            res_begin = cmd.z_begin(url, tags)
            respons.append(res_begin)
            try :
                resu = cmd.zone_ns_insert(tags)
            except Exception as e:
                respons = {
                    "Status" : False,
                    "Error" : str(e)
                }
                return response(400, message=respons )
            else:
                for i in resu:
                    http_response = utils.send_http(url,i)
                    respons.append(http_response)

                res_commit = cmd.z_commit(url,tags)
                respons.append(res_commit)
                return response(200, data=respons)

        if init_data['action'] == 'zone-srv-insert':
            result = list()
            for i in init_data['data']:
                tags = i['tags']
            begin_json = cmd.zone_begin_http(url, tags)
            # begin_respon = utils.send_http(url,begin_json)
            result.append(begin_json)

            try:
                respons = cmd.zone_insert_srv(tags)
            except Exception as e:
                respons = {
                    "status" : False,
                    "error": str(e)
                }
                return response(400, data=result, message=respons)
            else:
                http_response = utils.send_http(url,respons)
            
                result.append(http_response)

                commit_json = cmd.zone_commit_http(url, tags)
                # commit_response = utils.send_http(url,commit_json)
                result.append(commit_json)
                return response(200, data=result)

        if init_data['action'] == 'zone-mx-insert':
            result = list()
            for i in init_data['data']:
                tags = i['tags']

            begin_json = cmd.zone_begin_http(url, tags)
            # begin_respon = utils.send_http(url,begin_json)
            result.append(begin_json)

            try :
                respons = cmd.zone_insert_mx(tags)

            except Exception as e:
                respons = {
                    "status" : False,
                    "error": str(e)
                }
                return response(400, data=result, message=respons)
            else :
                http_response = utils.send_http(url,respons)
                result.append(http_response)

                commit_json = cmd.zone_commit_http(url, tags)
                # commit_response = utils.send_http(url,commit_json)
                result.append(commit_json)
                return response(200, data=result)

        # delete all zone
        if init_data['action'] == 'conf-unset':
            result = list()
            for i in init_data['data']:
                tags = i['tags']
            data = cmd.conf_unset(tags)
            cmd.conf_begin_http(url)
            http_respons = utils.send_http(url,data)
            cmd.conf_commit_http(url)
            return response(200, data=http_respons)
        
        if init_data['action'] == 'zone-unset':
            result = list()
            for i in init_data['data']:
                print(i)
                tags = i['tags']
            respons = list()
            res_begin = cmd.zone_begin_http(url,tags)
            respons.append(res_begin)
            json_command = cmd.zone_unset(tags)
            http_response = utils.send_http(url,json_command)
            respons.append(http_response)
            res_commit = cmd.zone_commit_http(url, tags)
            respons.append(res_commit)
            return response(200, data=respons)
