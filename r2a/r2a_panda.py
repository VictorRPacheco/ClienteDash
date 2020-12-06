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
        self.bandwidthShare = []
        self.downloadTime = []

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
        self.downloadTime.append(time.time())

        # Estimate the bandwidth share
        k = 0.14 # Probing convergence rate CONSTANT
        w = 0.3 # Probing additive increase bitrate  CONSTANT
        segmentDownloadTime = self.downloadTime[-1]-self.downloadTime[len(self.downloadTime)-2] # Calculate the time to download one segment (T~)
        throughputAferido = (self.throughputs[-1]) # get the last throughput measured
        actualInterRequestTime = max(1,segmentDownloadTime) # Calculate the actual inter request time (T)

        if(len(self.bandwidthShare) == 0):
            self.bandwidthShare.append(throughputAferido)
        else:
            self.bandwidthShare.append((throughputAferido-self.bandwidthShare[-1])/(actualInterRequestTime))
            #self.bandwidthShare.append(k*(w-max(0,self.bandwidthShare[-1]-throughputAferido+w)))

        print("throughputAferido>>>",throughputAferido)
        print("bandwidthShare>>>",self.bandwidthShare[-1])

        # Smooth out bandwidthShare to produce a filtered version
        avgBandwithShare = mean(self.bandwidthShare[-2:]) # Calculate the moving average

        # Quantize the avgBandwithShare to the discrete video bitrate
        selected_qi = self.qi[0]
        for i in self.qi:
            if avgBandwithShare > i:
                selected_qi = i

        print("QI>", self.qi[len(self.qi)-1])

        # Schedule the next download request


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
