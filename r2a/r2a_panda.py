from r2a.ir2a import IR2A
from player.parser import *
import time
from statistics import mean


class R2A_Panda(IR2A):

    def __init__(self, id):
        IR2A.__init__(self, id)
        self.throughputs = []
        self.request_time = 0
        self.qi = []

    def handle_xml_request(self, msg):
        self.request_time = time.perf_counter()
        self.send_down(msg)

    def handle_xml_response(self, msg):

        parsed_mpd = parse_mpd(msg.get_payload())
        self.qi = parsed_mpd.get_qi()

        t = time.perf_counter() - self.request_time
        self.throughputs.append(msg.get_bit_length() / t)
        self.send_up(msg)

    def handle_segment_size_request(self, msg):
        self.request_time = time.perf_counter()
        #avg = mean(self.throughputs) / 2
        throughputAferido = self.throughputs[len(self.throughputs)-1]
        print("throughputAferido >>>> ",throughputAferido)
        vazao = throughputAferido*0.7


        selected_qi = self.qi[0]
        for i in self.qi:
            if vazao > i:
                selected_qi = i

        print("QI>", self.qi[len(self.qi)-1])

        #print("teste")
        #print("Tamanho", self.whiteboard.get_playback_history())
        #buffer_size = self.Player.get_amount_of_video_to_play_without_lock()
        #print(self.whiteboard.add_playback_buffer_size(self.whiteboard.playback_buffer_size.get_items()))

        msg.add_quality_id(selected_qi)
        self.send_down(msg)

    def handle_segment_size_response(self, msg):
        t = time.perf_counter() - self.request_time
        self.throughputs.append(msg.get_bit_length() / t)
        self.send_up(msg)

    def initialize(self):
        pass

    def finalization(self):
        pass
