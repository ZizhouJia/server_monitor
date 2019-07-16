import paramiko
import re
import time

def get_nvidia_info(ssh):
    stdin,stdout,stderr=ssh.exec_command("nvidia-smi --query-gpu=name,utilization.gpu,utilization.memory,memory.used,memory.total --format=csv,noheader")
    output=stdout.read().decode('utf-8')
    # print(output)
    outputs=re.split(",|\n",output)
    cards=len(outputs)//5
    l=[]
    for i in range(0,cards):
         card_info={}
         card_info["id"]=i
         card_info["name"]=outputs[i*5]
         card_info["utilization"]=int(outputs[i*5+1][:-1])
         card_info["utilization_memory"]=int(outputs[i*5+2][:-1])
         card_info["memory_used"]=int(outputs[i*5+3][:-3])
         card_info["memory_total"]=int(outputs[i*5+4][:-3])
         l.append(card_info)
    return l

def get_memory_info(ssh):
    memory_info={}
    stdin,stdout,stderr=ssh.exec_command("free -m")
    output=stdout.read().decode('utf-8')
    outputs=re.split(" |\n",output)
    outputs=[output for output in outputs if len(output)!=0]
    memory_info["total"]=int(outputs[7])
    memory_info["available"]=int(outputs[12])
    return memory_info


class server_monitor_manager(object):
    def __init__(self,username,private_key_path="/home/jiazizhou/.ssh/id_rsa"):
        self._servers={}
        self._functions={}
        self.private_key_path=private_key_path
        self.username=username

    def register_server(self,name,ip_address):
        self._servers[name]=ip_address

    def register_function(self,info_name,function):
        self._functions[info_name]=function

    def get_single_server_info(self,ip_address):
        try:
            ssh=paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            pkey=paramiko.RSAKey.from_private_key_file(self.private_key_path)
            ssh.connect(hostname=ip_address,username=self.username,pkey=pkey)
            server_info={}
            # server_info["ip_address"]=ip_address
            for key in self._functions:
                try:
                    server_info[key]=self._functions[key](ssh)
                except Exception as e:
                    server_info[key]="device lost"
        except Exception as e:
            return "connect error"
        ssh.close()
        return server_info

    def get_all_server_info(self):
        all_info={}
        for key in self._servers:
            all_info[self._servers[key]]=self.get_single_server_info(self._servers[key])
        return all_info


if __name__=="__main__":
    manager=server_monitor_manager("jiazizhou")
    manager.register_server("42","166.111.80.42")
    manager.register_server("169","166.111.80.169")
    manager.register_function("GPU",get_nvidia_info)
    manager.register_function("memory",get_memory_info)
    print(manager.get_all_server_info())
    print(time.sleep(10))
    print(manager.get_all_server_info())






