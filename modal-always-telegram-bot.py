import modal
import os
import subprocess
import time
import modal
import json

app = modal.App("QuantLab")


cuda_version = "12.4.0"  # should be no greater than host CUDA version
flavor = "devel"  #  includes full CUDA toolkit
operating_sys = "ubuntu22.04"
tag = f"{cuda_version}-{flavor}-{operating_sys}"

image = "nvidia/cuda:12.4.0-devel-ubuntu22.04"

vol_name = "my-volume-1"
vol = modal.Volume.from_name(vol_name, create_if_missing=True)
vol_dir = f'/root/{vol_name}'

vol_name_2 = "backup"
vol_2 = modal.Volume.from_name(vol_name_2, create_if_missing=True)
vol_dir_2 = f'/root/{vol_name_2}'

imaged = (
    modal.Image.from_registry(f"nvidia/cuda:{tag}", add_python="3.11")
    .apt_install("git")
    .apt_install("openssh-server")
    .apt_install("curl")
    .apt_install("unzip")
    .apt_install("make")
    .apt_install("vim")
    .apt_install("python3-venv")
    .apt_install("cudnn9-cuda-12")
    .apt_install("rsync")
    .apt_install("autossh")
    .apt_install("redis-server")
    .apt_install("npm")
    .apt_install("nodejs")

# torch torchvision torchaudio polars requests scipy matplotlib altair tqdm vegafusion "vl-convert-python>=1.6.0" 
    .pip_install("torch", "torchvision", "torchaudio", "polars", "requests", "scipy", "matplotlib", "altair", "tqdm", "vegafusion", "vl-convert-python>=1.6.0")
    .pip_install("pyngrok")
    .pip_install("tensorflow[and-cuda]")
    .pip_install("jupyter")
    .pip_install("pybit")
    .pip_install("python-telegram-bot[job-queue]")
    .pip_install("requests")
    .pip_install("telethon")
    .pip_install("pandas")
    .pip_install("matplotlib")
    .pip_install("mpl_finance")
    .pip_install("torch")
    .pip_install("numpy")
    .pip_install("seaborn")
    .pip_install('pyarrow')
    .pip_install("Flask==3.0.0")
    .pip_install("redis==5.0.1")

    # .pip_install("mplfinance")

    .run_commands("mkdir /run/sshd")
    # REPLACE or ADD these lines for password login:
    .run_commands("echo 'root:0' | chpasswd") # Set your password #! NEVER CHANGE THIS it is neccessary for ssh to work
    .run_commands("echo 'PermitRootLogin yes' >> /etc/ssh/sshd_config") # Allow root login
    # Passwordless SSH: add public key to authorized_keys
    .run_commands("mkdir -p /root/.ssh && chmod 700 /root/.ssh")
    .run_commands("echo 'ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIJGwajhM0cXLIe0XnpBMzE7H93s564zCNh1QvvhS7n9k quantlab-modal' >> /root/.ssh/authorized_keys")
    .run_commands("chmod 600 /root/.ssh/authorized_keys")

    .run_commands("npm install n -g")
    .run_commands("n stable")
    .run_commands("wget -qO /usr/local/bin/ttyd https://github.com/tsl0922/ttyd/releases/download/1.7.7/ttyd.x86_64 && chmod +x /usr/local/bin/ttyd")
    # .run_commands("npm install -g 9router")

    .run_commands("curl -s https://syncthing.net/release-key.txt | apt-key add -")
    .run_commands("echo \"deb https://apt.syncthing.net/ syncthing stable\" | tee /etc/apt/sources.list.d/syncthing.list")
    .run_commands("apt update")
    .run_commands("apt install syncthing")

    .run_commands("curl -sS https://webinstall.dev/mutagen | bash")

    .run_commands("npm install -g localtunnel")
)

# gpu="T4"
timeout_period = 85600
NGROK_AUTHTOKEN = "39n9slLScRkgBd7shA5ZWUvfSf0_H3uRsHp8aAa11xF9nF19"
CHART_NGROK_AUTHTOKEN = "39nLfkTWMdtB4ODiRCiL511EDqe_7XeaLxcw6CMxxDZjXc3Ah"




# ["eu","uk","ap"]
@app.cls(region="eu", image=imaged,timeout=timeout_period,retries=10,max_containers=1,volumes={vol_dir: vol,vol_dir_2: vol_2},cpu=0.20,memory=1036)
class QuantLab:
    @modal.exit()
    def on_exit(self):
        os.system("python /root/my-volume-1/working/kucoin_bot/helper_scripts/save_home.py")
        print("Container exiting — the quantlab will be restarting ...")
        os.system("killall autossh 2>/dev/null; killall ssh 2>/dev/null")  # Release Serveo tunnels
        # asyncio.run(send_message('Container exiting — the quantlab will be restarting ....'))
        os.system('python3 modal_storage/telegram_message.py "Container exiting — the quantlab will be restarting ...."')

    @modal.method()
    def run(self):
        while True:
            # os.system("rsync -av /root/my-volume-1/root /root")
            # os.system("cp -r /root/my-volume-1/root /root/")
            os.system("python3 /root/my-volume-1/working/kucoin_bot/sync_home.py")
            # os.system("bash /root/my-volume-1/root/mutgen.sh")
            try:
                ngrok_port = "11223"
                jupyter_port = int(ngrok_port)
                def run_jupyter_server(port: str):
                    import IPython
                    import subprocess
                    from pyngrok import ngrok
                    from typing import Any, Dict, List, Optional
                    def setup_ngrok_tunnel(port: str) -> ngrok.NgrokTunnel:
                        ngrok_auth_token = NGROK_AUTHTOKEN #? ngrok token for modal
                        if not ngrok_auth_token:
                            raise RuntimeError("NGROK_AUTHTOKEN is not set.")
                        ngrok.set_auth_token(ngrok_auth_token)
                        tunnel = ngrok.connect(port, host_header=f'localhost:{port}')
                        return tunnel
                    return setup_ngrok_tunnel(port)
                import requests



                os.system("npm install -g 9router@latest")
                os.system("9router &")

                os.system("curl -s https://ngrok-agent.s3.amazonaws.com/ngrok.asc | tee /etc/apt/trusted.gpg.d/ngrok.asc >/dev/null && echo \"deb https://ngrok-agent.s3.amazonaws.com buster main\" | tee /etc/apt/sources.list.d/ngrok.list && apt update && apt install ngrok")
                # os.system(f"ngrok config add-authtoken {CHART_NGROK_AUTHTOKEN}")
                # os.system("ngrok http 8070 &")
                os.system("cd /root/my-volume-1/working/kucoin_bot/ && python3 -m http.server 8070 &")
                # tunnels = requests.get('http://localhost:4040/api/tunnels').json()
                # chart_ngrok_url = tunnels['tunnels'][0]['public_url']

                os.system("redis-server --daemonize yes")
                # os.system(f"autossh -M 0 -i /root/my-volume-1/serveo_key -R {DASHBOARD_SERVEO_ALIAS}:80:localhost:5000 serveo.net &")
                # os.system("autossh -M 0 -o 'StrictHostKeyChecking=no' -o 'ServerAliveInterval=30' -o 'ExitOnForwardFailure=yes' -i /root/my-volume-1/serveo_key -R quant-dashboard:80:localhost:5000 serveo.net &")
                os.system("cd /root/my-volume-1/working/kucoin_bot/dashboard && python app.py &")
                os.system("cd /root/my-volume-1/working/kucoin_bot/dashboard && python update_dashboard.py &")
                os.system("cd /root/my-volume-1/working/kucoin_bot/dependencies && python backup_and_send.py &")
                

                # os.system("zrok share public --share-token quant-chart &")
                os.system("ttyd -p 7681 -W /bin/bash &")
                os.system("curl -sSf https://sshx.io/get | sh")
                os.system("sshx &")
                os.system("curl -Lk 'https://code.visualstudio.com/sha/download?build=stable&os=cli-alpine-x64' --output vscode_cli.tar.gz && tar -xf vscode_cli.tar.gz")
                os.system("git clone https://github.com/A7med-Hosam/modal_storage.git")
                # os.system("python modal_storage/server-start.py")
                os.system('python /root/my-volume-1/working/kucoin_bot/dependencies "Quant Lab is Live"')
                print("Quant Lab is Live")

                # ? ./code tunnel

                # Start SSH daemon in background
                # Note that the ssh password is '0' and the username is 'root'

                # os.system("9router &")
                os.system("/usr/sbin/sshd -D -e &")
                # Start Serveo SSH tunnel with stable alias (always: ssh -J serveo.net root@quantlab)
                SERVEO_ALIAS = "quantlab"
                DASHBOARD_SERVEO_ALIAS = "dashboard-quantlab"
                FILES_BROWSER_SERVEO_ALIAS = "file-browser"
                JUPYTER_SERVEO_ALIAS = "jupyter-quantlab"
                N9ROUTER_ALIAS = "9router"
                SSHX_SERVEO_ALIAS = "terminal"
                
                # Generate a new SSH key mapped to a "new account" for Serveo
                os.system("if [ ! -f /root/my-volume-1/serveo_key_2 ]; then ssh-keygen -t rsa -b 2048 -f /root/my-volume-1/serveo_key_2 -q -N ''; fi")
                os.system("if [ ! -f /root/my-volume-1/serveo_key_3 ]; then ssh-keygen -t rsa -b 2048 -f /root/my-volume-1/serveo_key_3 -q -N ''; fi")
                os.system("if [ ! -f /root/my-volume-1/serveo_key_4 ]; then ssh-keygen -t rsa -b 2048 -f /root/my-volume-1/serveo_key_4 -q -N ''; fi")
                os.system("if [ ! -f /root/my-volume-1/serveo_key_5 ]; then ssh-keygen -t rsa -b 2048 -f /root/my-volume-1/serveo_key_5 -q -N ''; fi")
                time.sleep(4)
                os.system(f"autossh -M 0 -o 'StrictHostKeyChecking=no' -o 'ServerAliveInterval=30' -i /root/my-volume-1/serveo_key -R {DASHBOARD_SERVEO_ALIAS}:80:localhost:5000 serveo.net &")
                # os.system(f"autossh -M 0 -o 'StrictHostKeyChecking=no' -o 'ServerAliveInterval=30' -i /root/my-volume-1/serveo_key_2 -R {FILES_BROWSER_SERVEO_ALIAS}:80:localhost:8070 serveo.net &")
                os.system(f"autossh -M 0 -o 'StrictHostKeyChecking=no' -o 'ServerAliveInterval=30' -i /root/my-volume-1/serveo_key_3 -R {N9ROUTER_ALIAS}:80:localhost:20128 serveo.net &")
                os.system(f"autossh -M 0 -o 'StrictHostKeyChecking=no' -o 'ServerAliveInterval=30' -i /root/my-volume-1/serveo_key_4 -R {SSHX_SERVEO_ALIAS}:80:localhost:7681 serveo.net &")
                # autossh -M 0 -o 'StrictHostKeyChecking=no' -o 'ServerAliveInterval=30' -i /root/my-volume-1/serveo_key_3 -R 9router:80:localhost:20128 serveo.net
                # autossh -M 0 -o 'StrictHostKeyChecking=no' -o 'ServerAliveInterval=30' -i /root/my-volume-1/serveo_key_2 -R jupyter-quantlab:80:localhost:11223 serveo.net
                # os.system(f"lt --port {jupyter_port} --subdomain jupyter-quantlab &")
                # os.system("lt --port 5000 --subdomain dashboard-quantlab &")
                # autossh -M 0 -o 'StrictHostKeyChecking=no' -o 'ServerAliveInterval=30' -i serveo_key_1 -R 9remote:80:localhost:2208 serveo.net

                # Open both tunnels concurrently (SSH as fallback + Jupyter)
                with modal.forward(port=22, unencrypted=True) as ssh_tunnel, \
                    modal.forward(port=jupyter_port, unencrypted=True) as jupyter_tunnel:
                    time.sleep(2)
                    os.system(f"autossh -M 0 -o 'StrictHostKeyChecking=no' -o 'ServerAliveInterval=30' -i /root/my-volume-1/serveo_key_2 -R {JUPYTER_SERVEO_ALIAS}:80:localhost:{jupyter_port} serveo.net &")
                    os.system(f"autossh -M 0 -o 'StrictHostKeyChecking=no' -o 'ServerAliveInterval=30' -o 'ExitOnForwardFailure=yes' -R {SERVEO_ALIAS}:22:localhost:22 serveo.net &")
                    # ngrok_tunnel = run_jupyter_server(ngrok_port)
                    # # SSH Connection Info (static via Serveo + modal fallback)
                    connection_cmd = f'ssh -J serveo.net root@{SERVEO_ALIAS}'
                    ssh_host, ssh_port = ssh_tunnel.tcp_socket
                    fallback_cmd = f'ssh -p {ssh_port} root@{ssh_host}'
                    
                    # Start Jupyter notebook in background
                    jupyter_process = subprocess.Popen(
                            [
                                "jupyter",
                                "notebook",
                                "--no-browser",
                                "--allow-root",
                                "--ip=0.0.0.0",
                                f"--port={jupyter_port}",
                                "--NotebookApp.allow_origin='*'",
                                "--NotebookApp.allow_remote_access=1",
                                "--NotebookApp.token=''",
                                "--NotebookApp.password=''",
                                "--allow-root",
                            ],
                        )


                    time.sleep(2)

                    # Keep both services running for the duration of the container's life
                    try:
                        end_time = time.time() + timeout_period
                        print(f"SSH (Serveo, static): {connection_cmd}  (password: 0)")
                        print(f"SSH (Modal, fallback): {fallback_cmd}  (password: 0)")
                        print(f"Jupyter available at => {jupyter_tunnel.url}")
                        print(f"ngrok tunnel created: https://{JUPYTER_SERVEO_ALIAS}.serveousercontent.com")
                        print(f"Dashboard URL: https://{DASHBOARD_SERVEO_ALIAS}.serveousercontent.com")
                        print(f"Files Browser URL: https://{FILES_BROWSER_SERVEO_ALIAS}.serveousercontent.com")
                        print(f"9router URL: https://{N9ROUTER_ALIAS}.serveousercontent.com")
                        print(f"SSHX (Web Terminal) URL: https://{SSHX_SERVEO_ALIAS}.serveousercontent.com")
                        print(f"Dashboard URL: https://{DASHBOARD_SERVEO_ALIAS}.loca.lt")
                        print(f"Jupyter URL: https://{JUPYTER_SERVEO_ALIAS}.loca.lt")
                        
                        while True:
                            try:
                                os.system("python /root/my-volume-1/working/kucoin_bot/bots_manager.py")
                            except Exception as e:
                                print(f"Error in bots_manager.py: {e}")
                            time.sleep(5)
                            break
                        while time.time() < end_time:
                            time.sleep(5)
                    except KeyboardInterrupt:
                        print("Interrupted by user, shutting down...")
                    finally:
                        jupyter_process.kill()
                        print("Jupyter process terminated.")
                # modal run --detach modal_storage\modal-always-telegram-bot.py
                # kill -9 53 && python modal_storage/telegramBotTest.py
                # +201016798636
                return
            except Exception as e:
                print(f"Error in quant_lab: {e}")
                time.sleep(5)
            
            # break

@app.local_entrypoint()
def main():
    print(f"⚡️ starting interruptible 🤖 Quant Lab")
    QuantLab().run.spawn().get()
