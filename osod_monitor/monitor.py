import multiprocessing

from pySerialTransfer import pySerialTransfer as txfer

from osod_monitor.payloads import (
    PayloadType,
    RequestedState,
    EstimatedState,
)


class Monitor:

    def __init__(self, port: str, baud: int = 115200):
        self.port = port
        self.baud = baud
        self.link: txfer.SerialTransfer | None = None
        self.running = multiprocessing.Value("b", False)
        self.process: multiprocessing.Process | None = None
        self.input_queue = multiprocessing.Queue()
        self.output_queue = multiprocessing.Queue()

    def open(self):
        if self.link is not None:
            self.link.open()

    def close(self):
        if self.link is not None:
            self.link.close()

    def start(self):
        self.running = True
        self.process = multiprocessing.Process(target=self.run)
        self.process.start()

    def stop(self):
        self.running = False
        if self.process is not None:
            self.process.join()

    def run(self):
        self.link = txfer.SerialTransfer(port=self.port, baud=self.baud)
        self.link.open()
        try:
            while self.running:
                self.process_outgoing_messages()
                self.process_incoming_messages()
        except KeyboardInterrupt:
            self.running = False
        # link is no longer running, so close it
        self.link.close()

    def process_outgoing_messages(self):
        if not self.input_queue.empty():
            data = self.input_queue.get()
            # TODO: process data

    def process_incoming_messages(self):
        if self.link.available():
            if self.link.status < 0:
                if self.link.status == txfer.CRC_ERROR:
                    print("ERROR: CRC_ERROR")
                elif self.link.status == txfer.PAYLOAD_ERROR:
                    print("ERROR: PAYLOAD_ERROR")
                elif self.link.status == txfer.STOP_BYTE_ERROR:
                    print("ERROR: STOP_BYTE_ERROR")
                else:
                    print("ERROR: {}".format(self.link.status))
                return

            msg_type = self.link.rx_obj(obj_type="c", byte_format="<")

            payload = None
            match int.from_bytes(msg_type):
                case PayloadType.REQUESTED_STATE.value:
                    payload_bytes = bytes(self.link.rxBuff[1 : (1 + 8)])
                    payload = RequestedState.from_bytes(payload_bytes)
                case PayloadType.ESTIMATED_STATE.value:
                    payload_bytes = bytes(self.link.rxBuff[1 : (1 + 32)])
                    payload = EstimatedState.from_bytes(payload_bytes)
                case _:
                    payload = None

            if payload:
                self.output_queue.put(payload)

    def send(self, data):
        self.input_queue.put(data)

    def receive(self):
        if not self.output_queue.empty():
            return self.output_queue.get()
        else:
            return None
