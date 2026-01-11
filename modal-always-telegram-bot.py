import modal
import os

app = modal.App("QuantLab")

secret = modal.Secret.from_name("aws-secret1")

cuda_version = "12.4.0"  # should be no greater than host CUDA version
flavor = "devel"  #  includes full CUDA toolkit
operating_sys = "ubuntu22.04"
tag = f"{cuda_version}-{flavor}-{operating_sys}"

vol_name = "my-volume-1"
vol = modal.Volume.from_name(vol_name, create_if_missing=True)
vol_dir = f'/root/{vol_name}'

imaged = (
    modal.Image.from_registry(f"nvidia/cuda:{tag}", add_python="3.11")
    .apt_install("git")
    .apt_install("curl")
    .apt_install("make")
    .apt_install("vim")
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
    
    # .pip_install("mplfinance")
)

@app.function(region="eu",image=imaged,timeout=84600,retries=10,volumes={vol_dir: vol})
def quant_lab(): 
    print("Quant Lab is Live")
    os.system("curl -sSf https://sshx.io/get | sh")
    os.system("curl -Lk 'https://code.visualstudio.com/sha/download?build=stable&os=cli-alpine-x64' --output vscode_cli.tar.gz && tar -xf vscode_cli.tar.gz")
    os.system("git clone https://github.com/A7med-Hosam/modal_storage.git")
    os.system("python modal_storage/server-start.py && sshx")
    # modal run --detach modal_storage\modal-always-telegram-bot.py
    # kill -9 53 && python modal_storage/telegramBotTest.py
    # +201016798636
    return



