# -*- coding: utf-8 -*-
"""
@author: Marcos F. Caetano (mfcaetano@unb.br) 11/03/2020

@description: PyDash Project

Whiteboard structure to deliver statistical information
from the Player to the R2A algorithms.
"""


class Whiteboard:
    __instance = None

    @staticmethod
    def get_instance():
        if Whiteboard.__instance is None:
            Whiteboard()
        return Whiteboard.__instance

    def __init__(self):
        if Whiteboard.__instance is not None:
            raise Exception('This class is a singleton!')
        else:
            Whiteboard.__instance = self
            self.playback = []
            self.playback_qi = []
            self.playback_pauses = []
            self.playback_buffer_size = []

    def add_playback_qi(self, playback_qi):
        self.playback_qi = playback_qi

    def add_playback_pauses(self, pauses):
        self.playback_pauses = pauses

    def add_playback_buffer_size(self, buffer_size):
        self.playback_buffer_size = buffer_size

    def add_playback_history(self, playback):
        self.playback = playback

    def get_playback_qi(self):
        """
        It returns a tuples list of time and QI's segments already played by the Player.
        The time represents the moment when a QI segment was consumed (played) by the Player.
        """
        return self.playback_qi

    def get_playback_pauses(self):
        """
        It returns a tuples list of time and pauses happened during the playing of
        the video. The time (s) represents the moment when a video pause occurred and
        the pauses represents the lenght of this pauses.
        """
        return self.playback_pauses

    def get_playback_buffer_size(self):
        """
        It returns a tuples list of time and buffer size during the playing video.
        The time represents the moment when the buffer size was measured.
        """
        return self.playback_buffer_size


    def get_playback_history(self):
        """
        It returns a tuples list of time and playback history happened during
        the playing video. The time represents the moment when was measured the possible
        to play or not the video. For playback, the number one means it was possible to
        play and zero is otherwise.
        """
        return self.playback
