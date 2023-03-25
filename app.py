import subprocess


from lofi_generator import trainer


from flask import Flask


api = Flask(__name__)


@api.route("/")
def hello_world():
    return "Welcome to the Lofi Generator! :)"


@api.route("/generate_music")
def generate_music():
    print("Generating music...")
    subprocess.run(["python", "-m", "lofi_generator"])


# TODO: Make this endpoint private
# Will need proper access tokens to reach
@api.route("/train_network")
def train_network():
    print("Train Network...")
    trainer.train_network()


if __name__ == "__main__":
    api.run(host="0.0.0.0", port=3000)
