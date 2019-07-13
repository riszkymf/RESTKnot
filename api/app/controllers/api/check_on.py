from flask_restful import Resource, request
from app.helpers.rest import response
from app.models import model
from app.helpers import check_on_sync


class NotifyOnAgent(Resource):
    def post(self):
        result = list()
        data = request.get_json(force=True)
        status_agent = data['status_agent']
        nm_host = data['nm_host']
        data_zone_agent = data['data_zone']
        try:
            zone_data = model.get_all("zn_zone")
        except Exception as e:
            return response(401, message=str(e))
        if status_agent == "slave":
            url_data = None
            try:
                url_data = model.get_by_id("v_cs_slave_node", "nm_slave_node", nm_host)[0]
            except Exception as e:
                return response(401, message=str(e))
            urls = "http://"+url_data['ip_slave_node']+":"+url_data['port_slave_node']+"/api/command_rest"
            for i in zone_data:
                if i['nm_zone'] not in data_zone_agent:
                    params = {
                        "urls": urls,
                        "data_zone": i,
                        "nm_master": url_data['nm_master']
                    }
                    slave = check_on_sync.sync_task_slave.delay(params)
                    result.append({
                        "id": str(slave),
                        "state": slave.state
                    })
                    print(result)
        
        if status_agent== "master":
            try:
                url_data = model.get_by_id("cs_master", "nm_master", nm_host)[0]
            except Exception as e:
                print(e)
            urls = "http://"+url_data['ip_master']+":"+url_data['port']+"/api/command_rest"
            for i in zone_data:
                if i['nm_zone'] not in data_zone_agent:
                    params = {
                        "urls": urls,
                        "data_zone": i,
                        "nm_master": url_data['nm_master'],
                        "nm_config": url_data['nm_config']
                    }
                    master = check_on_sync.sync_task_master.delay(params)
                    result.append({
                        "id": str(master),
                        "state": master.state
                    })
        return response(200, data=result, message="Syncronizning Process")