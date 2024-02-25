# SPDX-FileCopyrightText: 2021 Kattni Rembor for Adafruit Industries
#
# SPDX-License-Identifier: MIT

"""
CircuitPython single MP3 playback example for Raspberry Pi Pico.
Plays a single MP3 once.
"""
import board
import audiomp3
import audiopwmio

audio = audiopwmio.PWMAudioOut(board.GP0)

mp3files = ["blue.mp3", "redF.mp3", "greenF.mp3", "yellowF.mp3"]

mp3 = open(mp3files[0], "rb")
decoder = audiomp3.MP3Decoder(mp3)

for filename in mp3files:
    decoder.file = open(filename, "rb")
    audio.play(decoder)
    print("Playing:", filename)
    while audio.playing:
        pass

print("Done playing!")
