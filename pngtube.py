import PIL.Image as PIL
import aubio
import pygame
import pygame_widgets
from pygame_widgets.slider import Slider
from pygame_widgets.button import Button
from pygame_widgets.dropdown import Dropdown
from pygame_widgets.textbox import TextBox
import pyaudio
import numpy as np
import glob
import random
import cv2
from tkinter import filedialog
import ctypes
import os


METHOD = 'default'
PERIOD_SIZE_IN_FRAME = 2048
p = pyaudio.PyAudio()
try:
    f = open('config.cfg', 'r')
    PATH = f.readline()[:-1]
    first_file = f.readline()[:-1]
    filetag = f.readline()[:-1]
    device_index = int(f.readline()[:-1])
    data_volume = float(f.readline())
except FileNotFoundError:
    PATH = filedialog.askdirectory(title="Valitse kansio, jossa kuvat ovat.")
    if PATH == "":
        exit()
    first_file = glob.glob(f"{PATH}/*00000.png")[-1]
    filetag = first_file.split("\\")[-1].split("_")[0]
    data_volume = 0.2

with PIL.open(first_file) as img:
    img_size = img.size

pygame.init()

size = width, height = img_size
flags = pygame.RESIZABLE
clock = pygame.time.Clock()
screen = pygame.display.set_mode(size,flags)

avatars = []
for image in glob.glob(f"{PATH}/{filetag}*.png"):
    avatars.append(pygame.image.load(image))

step_prev = 0
step = 0
steps = len(avatars)-1

screen.fill((255,255,255))
screen.blit(avatars[0],(0,0))


slider = Slider(screen,round(height/20),round(width/1.6),800,20,min=0,max=10,step=0.02,initial=data_volume)
output = TextBox(screen,round(height*1.55),round(width/1.62),45,30,fontSize=20)
output.disable()

pygame.display.set_caption("pngTube")

pygame.display.update()

n=0

p = pyaudio.PyAudio()
info = p.get_host_api_info_by_index(0)
numdevices = info.get('deviceCount')

devices = []
device_indeces = []

for i in range(0,numdevices):
    if p.get_device_info_by_host_api_device_index(0,i).get("maxInputChannels") > 0:
        devices.append(str(i)+' '+p.get_device_info_by_host_api_device_index(0,i).get("name"))
        device_indeces.append(i)

dropdown = Dropdown(
screen,955,10,100,50,name="Devices",choices=devices,borderRadius=3,
colour="red",values=device_indeces,direction='down',
textHAlign='left'
)


font = pygame.font.SysFont('calibri',20)

initial_setup=False
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            break
    data_volume = slider.getValue()
    output.setText(data_volume)
    if dropdown.getSelected() is not None and chosen != int(dropdown.getSelected()):
        chosen = int(dropdown.getSelected())
        p=pyaudio.PyAudio()
        mic = p.open(
           format = pyaudio.paFloat32,channels=1,
           rate = 48000, input=True,
           frames_per_buffer=PERIOD_SIZE_IN_FRAME,
           input_device_index=chosen
           )
    elif dropdown.getSelected() is None and initial_setup ==False:
        if initial_setup == False:
            try:
                chosen = device_index
                p=pyaudio.PyAudio()
                mic = p.open(
                       format = pyaudio.paFloat32,channels=1,
                       rate = 48000, input=True,
                       frames_per_buffer=PERIOD_SIZE_IN_FRAME,
                       input_device_index=chosen
                       )
                initial_setup = True
            except NameError:
                chosen = 1
                p=pyaudio.PyAudio()
                mic = p.open(
                       format = pyaudio.paFloat32,channels=1,
                       rate = 48000, input=True,
                       frames_per_buffer=PERIOD_SIZE_IN_FRAME,
                       input_device_index=chosen
                       )
                pygame.display.flip()
                pygame_widgets.update(event)
                initial_setup = True
                continue
    data=mic.read(PERIOD_SIZE_IN_FRAME)
    samples = np.frombuffer(data,dtype=aubio.float_type)
    volume = (np.sum(samples * samples) / len(samples)) * 1000
    step = n+1
    n+=1
    if n >= steps:
        n = 0
        step = 1
    if step_prev != step:
        screen.fill((255,255,255))
        step_prev = step
        if volume < slider.getValue():
            screen.blit(avatars[0], (0,0))
        else:
            screen.blit(avatars[step],(0,0))
    text =font.render(str(round(volume,2)),True,(0,0,0))
    screen.blit(text,(800,10+height))
    pygame_widgets.update(event)
    pygame.display.flip()
    clock.tick(60)
pygame.quit()

f = open('config.cfg', 'w')
f.write(PATH+"\n")
f.write(first_file+"\n")
f.write(filetag+"\n")
f.write(str(chosen)+"\n")
f.write(str(slider.getValue()))
f.close()
