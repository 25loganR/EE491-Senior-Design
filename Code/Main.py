from mfrc522 import MFRC522
import neopixel
from machine import Pin, Timer
from wavePlayer import wavePlayer
import os as uos
import utime

reader = MFRC522(spi_id=0,sck=2,miso=4,mosi=3,cs=1,rst=0)
key = [0xFF,0xFF,0xFF,0xFF,0xFF,0xFF]
absoluteBlock=8   #AB = sector * 4 + (block % 4)

numLeds = 97
pixels = neopixel.NeoPixel(machine.Pin(15), numLeds)
reversed_neopixels = neopixel.NeoPixel(machine.Pin(15), numLeds)
pixels.fill((0,0,0))
pixels.write()

colors = [(0, 0, 0),(0, 255, 0),(0, 128, 128),(93, 162, 0),(0, 0, 255),(45, 210, 0),(255, 0, 0),(30,230,24),(255,255,255)]   #Off,Red,Purple,Yellow,Blue,Orange,Green,Pink,White
track = ['R', 'P', 'Y', 'B', 'O', 'G', 'R', 'P', 'S', 'Y', 'B', 'O', 'G', 'R', 'P', 'Y', 'B', 'O', 'G', 'S', 'R', 'P', 'Y', 'B', 'O', 'G', 'R', 'P', 'Y', 'B', 'O', 'G', 'R', 'P', 'Y', 'B', 'S', 'O', 'G', 'R', 'P', 'Y', 'B', 'O', 'G', 'R', 'P', 'Y', 'B', 'O', 'G', 'R', 'P', 'Y', 'B', 'S', 'O', 'G', 'R', 'P', 'Y', 'B', 'O', 'G', 'R', 'P', 'Y', 'B', 'O', 'S', 'G', 'R', 'P', 'Y', 'B', 'O', 'G', 'R', 'P', 'Y', 'B', 'O', 'G', 'R', 'P', 'Y', 'S', 'B', 'O', 'G', 'R', 'P', 'Y', 'B', 'O', 'G', 'W']
cardVal = [' ','R','P','Y','B','O','G','S','W','F']

playerPos = []   #Player 1-4 starting position
playerNames = []             #Initate player names append them later

tim = tim=Timer(-1)
audio = wavePlayer()

char = ['C2','C4','C1','C3']
charaud = ['/sounds/Gummy Bear.wav', '/sounds/Chocolate.wav','/sounds/Donut.wav','/sounds/Gingerbread Man.wav']
audpath = dict(zip(char, charaud))
cardpath = [' ', '/sounds/Red Heart.wav','/sounds/Purple Flower.wav','/sounds/Yellow Star.wav','/sounds/Blue Square.wav','/sounds/Orange Circle.wav','/sounds/Green Triangle.wav']
specpath = ['/sounds/Peanut.wav','/sounds/Lollipop.wav','/sounds/Candy cane.wav','/sounds/Snowflake.wav','/sounds/Ice cream.wav','/sounds/Cupcake.wav']

def dispTrack(isBlink):
    for step in range(40):
        for i, letter in enumerate(track):
            index = cardVal.index(letter)
            color = tuple(int(val * (step / 40)) for val in colors[index])
            if isBlink and i == playerPos[player-1]: continue
            pixels[i] = color
        writePath()
        utime.sleep_ms(1)

def shortcut(num):
    if num == 1:
        audio.play('/sounds/Rainbow trail.wav')
        utime.sleep_ms(600)
        target_color = (45, 210, 0)
        for step in range(40):
            pixels[4] = tuple(int(channel * (40 - step) / 40) for channel in pixels[4])
            pixels[43] = tuple(int((channel * step + target_color[index] * (40 - step)) / 40) for index, channel in enumerate(pixels[43]))
            writePath()
            utime.sleep_ms(1)    
        playerPos[player] = 43
    elif num == 2:
        audio.play('/sounds/Lollipop pass.wav')
        utime.sleep_ms(600)
        target_color = (93, 162, 0)
        for step in range(40):
            pixels[20] = tuple(int(channel * (40 - step) / 40) for channel in pixels[20])
            pixels[28] = tuple(int((channel * step + target_color[index] * (40 - step)) / 40) for index, channel in enumerate(pixels[28]))
            writePath()
            utime.sleep_ms(1)   
        playerPos[player] = 28

def calcPos(data, player):
    prev = playerPos[player]
    if data[0] == 'S':
        sCount = 0
        for i, val in enumerate(track):
            if val == 'S':
                sCount += 1
                if sCount == int(data[1]):
                    playerPos[player] = i
                    break
        audio.play('/sounds/Go to the.wav')
        audio.play(specpath[sCount-1])
    else:
        try:
            nextIndex = track.index(data[0], playerPos[player] + 1)
            if int(data[1]) == 2:
                nextIndex = track.index(data[0], nextIndex + 1)
            playerPos[player] = nextIndex
        except ValueError:
            playerPos[player] = track.index('W', playerPos[player]+1)
        if int(data[1]) == 1:
            audio.play('/sounds/Move 1.wav')
        elif int(data[1]) == 2:
            audio.play('/sounds/Move 2.wav')
        audio.play(cardpath[cardVal.index(data[0])])
        if playerPos[player] == (numLeds-1):
            playWin(prev)
    return prev

def blink(t):
    color = colors[cardVal.index(track[playerPos[player-1]])]
    if playerPos[player-1] >= 0:
        if pixels[playerPos[player-1]] == (0, 0, 0):
            pixels[playerPos[player-1]] = color  # Turn on the next position
        else:
            pixels[playerPos[player-1]] = (0, 0, 0)  # Turn off the next position
        writePath()

def animTrack(start, stop, color, win):
    global player
    for step in range(40):
        for i in range(numLeds):
            pixels[i] = tuple(int(channel * (40 - step) / 40) for channel in pixels[i])
        if start >= 0: pixels[start] = color
        writePath()
        utime.sleep_ms(1)
    pixels.fill((0, 0, 0))
    if start >= 0: pixels[start] = color
    writePath()

    tLen = 3
    direction = 1 if start <= stop else -1
    index = start-(tLen-1) if start <= stop else start
    while (index <= stop and direction == 1) or (index >= stop-(tLen-1) and direction == -1):
        pixels.fill((0,0,0))
        for j in range(tLen):
            if 0<=index+j<=numLeds-1 and (start<=index+j<=stop or stop<=index+j<=start): pixels[index + j] = color
        writePath()  
        utime.sleep_ms(50)
        index += direction
    if playerPos[player] == 4:
        shortcut(1)
    elif playerPos[player] == 20:
        shortcut(2)
    player = (player+1) % len(playerNames)
    if win == False:
        tim.init(mode=Timer.PERIODIC, period=400, callback=blink)
        dispTrack(True)
    
def writePath():
    # Create a new NeoPixel object with the same pin and number of LEDs
    
    # Fill the new NeoPixel object with reversed colors
    for i in range(numLeds):
        reversed_neopixels[i] = pixels[numLeds - i - 1]
    reversed_neopixels.write()    
        
def wheel(pos):
    if pos < 0 or pos > 255:
        return (0, 0, 0)
    if pos < 85:
        return (255 - pos * 3, pos * 3, 0)
    if pos < 170:
        pos -= 85
        return (0, 255 - pos * 3, pos * 3)
    pos -= 170
    return (pos * 3, 0, 255 - pos * 3)

def playWin(prev):
    animTrack(prev, numLeds-1, (255,255,255), True)
    audio.play(audpath[playerNames[player-1]])
    audio.play('/sounds/Wins.wav')
    while True:
        for j in range(255):
            for i in range(numLeds):
                rc_index = (i * 256 // numLeds) + j
                pixels[i] = wheel(rc_index & 255)
            writePath()
            utime.sleep_ms(10)

def scanRFID():
    while True:
        global scanning
        reader.init()
        (status, tag_type) = reader.request(reader.REQIDL)
        if status == reader.OK:
            try:
                tim.deinit()
                if playerPos[player-1] >= 0:
                    pixels[playerPos[player-1]] = colors[cardVal.index(track[playerPos[player-1]])] #Reset color
                    writePath()
            except:
                pass
            (status, uid) = reader.SelectTagSN()
            if status == reader.OK:
                status = reader.auth(reader.AUTHENT1A, absoluteBlock, key, uid)
                if status != reader.OK:
                    (status, tag_type) = reader.request(reader.REQIDL)
                    (status, uid) = reader.SelectTagSN()
                if status == reader.OK:
                    status, recv = reader.read(8)
                    if status == reader.OK:
                        data = ''.join(chr(byte) for byte in recv[:2])
                        if scanning or data[0] != 'C':
                            return(data)
                        elif ~scanning and data[0] == 'C':
                            tim.init(mode=Timer.PERIODIC, period=400, callback=blink)
        

    
dispTrack(False)
scanning = True
player = 0
while True:
    data = scanRFID()
    if data[0] == 'C' and scanning:
        if data not in playerNames:
            playerNames.append(data)
            playerPos.append(-1)
            audio.play(audpath[data])
            audio.play('/sounds/Added.wav')
            utime.sleep_ms(700)
    else:
        if len(playerNames) >= 1:
            scanning = False
            prev = calcPos(data, player)
            animTrack(prev, playerPos[player], colors[cardVal.index(data[0])], False)
            audio.play(audpath[playerNames[player]])
            audio.play('/sounds/Turn.wav')





