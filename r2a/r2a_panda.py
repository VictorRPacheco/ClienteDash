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
        self.targetInterRequestTime = [1]

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
        segmentDownloadTime = self.downloadTime[-1]-self.downloadTime[len(self.downloadTime)-2] # Calculate the time to download one segment
        throughputAferido = (self.throughputs[-1]) # get the last throughput measured
        actualInterRequestTime = max(self.targetInterRequestTime[-1],segmentDownloadTime) # Calculate the actual inter request time

        if(len(self.bandwidthShare) == 0):
            self.bandwidthShare.append(throughputAferido)
        else:
            self.bandwidthShare.append(((throughputAferido-self.bandwidthShare[-1])/(actualInterRequestTime)))

        # Smooth out bandwidthShare to produce a filtered version
        smoothBandwithShare = mean(self.bandwidthShare[-2:]) # Calculate the moving average
        if(smoothBandwithShare > self.bandwidthShare[-1]):
            smoothBandwithShare = self.bandwidthShare[-1]

        # Quantize the avgBandwithShare to the discrete video bitrate
        selected_qi = self.qi[0]
        for i in self.qi:
            if smoothBandwithShare > i:
                selected_qi = i

        print("QI>", self.qi[len(self.qi)-1])

        # Schedule the next download request
        B = 0.2  # Client buffer convergence rate CONSTANT
        bufferMin = 20 # Min buffer CONSTANT

        bufferSizeTuple = self.whiteboard.get_playback_buffer_size()

        if(len(bufferSizeTuple)>0):
            bufferSize = bufferSizeTuple[-1][1]
        else:
            bufferSize = 0


        self.targetInterRequestTime.append((selected_qi/smoothBandwithShare)+(B*(bufferMin - bufferSize)))

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
