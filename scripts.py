import subprocess

from lofi_generator import lstm

def generate_music():
    print("Generating music...")
    subprocess.run(["python", "-m", "lofi_generator"])


def train_network():
    print("Training network...")
    lstm.train_network()
