import json
from flask import Flask
from flask_apscheduler import APScheduler

import device_monitor

app=Flask(__name__)

manager=device_monitor.server_monitor_manager("jiazizhou","/home/jiazizhou/.ssh/id_rsa")
manager.register_server("42","166.111.80.42")
manager.register_server("169","166.111.80.169")
manager.register_function("GPU",device_monitor.get_nvidia_info)
manager.register_function("memory",device_monitor.get_memory_info)
target=manager.get_all_server_info()
target=json.dumps(target)
print(target)

def update_target():
    print("update server info")
    global target
    target=manager.get_all_server_info()
    target=json.dumps(target)
    # print(target)

@app.route("/")
def root():
    return "hello world"

@app.route("/get_info")
def get_info():
    print(target)
    return target


if __name__=="__main__":
    scheduler=APScheduler()
    scheduler.add_job(func=update_target,id="1",trigger='interval',seconds=10,replace_existing=True)
    scheduler.init_app(app)
    scheduler.start()
    app.run(debug=False,host="166.111.80.160",port=417)
