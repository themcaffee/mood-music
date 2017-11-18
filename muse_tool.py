import argparse

from pythonosc import dispatcher
from pythonosc import osc_server


TICK_AVG = 10
AVERAGE_FILE = "mellow_avg"


class MuseServer():
    def __init__(self, ip, port):
        self.tick = 0
        self.running_total = 0
        self.ip = ip
        self.port = port

        # Setup the OSC server
        self.dispatcher = dispatcher.Dispatcher()
        self.dispatcher.map("/debug", print)
        self.dispatcher.map("/muse/elements/experimental/mellow", self.mellow_handler, "EEG")

        self.server = osc_server.ThreadingOSCUDPServer(
            (args.ip, args.port), self.dispatcher)

    def mellow_handler(self, unused_addr, args, score):
        """
        Handles a new mellow value by averaging it and writing to a file
        :param unused_addr:
        :param args:
        :param score:
        :return:
        """
        self.running_total += score
        if self.tick == TICK_AVG:
            # Calculate and print the average
            avg = self.running_total / (TICK_AVG + 1)
            print("Mellow score: {}".format(avg))
            # Print out to file
            with open(AVERAGE_FILE, 'w') as f:
                f.write(str(avg))
            # Reset the average
            self.running_total = 0
            self.tick = 0
        else:
            self.tick += 1

    def run_server(self):
        print("Serving on {}:{}".format(self.ip, self.port))
        self.server.serve_forever()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--ip",
                        default="127.0.0.1",
                        help="The ip to listen on")
    parser.add_argument("--port",
                        type=int,
                        default=5000,
                        help="The port to listen on")
    args = parser.parse_args()

    server = MuseServer(args.ip, args.port)
    server.run_server()
