import sys # Zum Beenden des Programms
import pygame # Pygame Bibliothek
from scipy.io import wavfile # Bibliothek zum Lesen von Wave-Dateien
from scipy.fft import fft # Bibliothek zum Berechnen der FFT
from math import sqrt, log, floor # Mathematische Funktionen

MUSIC_END = pygame.USEREVENT+1 # Event zum Beenden der Musik

FFT_SIZE = 1024 # Größe der FFT
pygame.mixer.music.set_endevent(MUSIC_END)
AMPLITUDE_SIZE = 1024

class Visualizer:
    def __init__(self, file):
        #pygame.init()
        self.width = 960 # Width of the Window
        self.height = 720 # Height of the Window
        self.file = file # File to be visualized : Wave file
        self.samplerate, self.data = wavfile.read(self.file) # Read the wave file and get the SampleRate (44100 hz) and raw data
        self.samples, self.channels = self.data.shape # Get the number of samples and channels

        # Do some preprocessing of the Data for visualization of the Wave-File
        self.normalized_data = self.data / (2 ** 15) # Normalize the data to be between -1 and 1
        if self.normalized_data.ndim != 2: # If the wave file is mono
            exit(1)

        self.wave_data = self.normalized_data[0::int(self.samples//(log(self.samples)*100))]  # not all samples are needed to show wave. every (log(self.samples)*100) is enough
        pygame.mixer.init(self.samplerate, -16, self.channels) # Initialize the mixer with the sample rate and number of channels
        pygame.font.init() # Initialize the font module
        self.font = pygame.font.Font(None, 12) # Set the font and size of the text
        self.music_offset = 0 # Offset to keep track of the music position
        self.music_length = self.samples/self.samplerate # duration of the wave file
        self.max_amplitude = 0

        self.running = True # Flag to check if the program is running
        pygame.display.set_caption('[Heterogenious Computing] Audio Visualizer - Mohadesa') # Set the title of the window
        self.screen = pygame.display.set_mode([self.width, self.height]) # Set the size of the window
        pygame.mixer.music.load(self.file) # Load the wave file to be played
        pygame.mixer.pause() # Pause the music to be played

        
    def event_loop(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False # If the user closes the window, stop the program
            if event.type == pygame.KEYDOWN:
                music_position = self.music_offset + (pygame.mixer.music.get_pos()/1000) # Convert Musicposition milliseconds to seconds
                if event.key == pygame.K_SPACE:
                    if pygame.mixer.music.get_busy():
                        pygame.mixer.music.pause()
                    else:
                        pygame.mixer.music.unpause()
                if event.key == pygame.K_LEFT: # Backwards
                    self.music_offset = int(max(0, music_position - 1))
                    pygame.mixer.music.play(0, self.music_offset)
                if event.key == pygame.K_RIGHT: # Forward
                    self.music_offset = int(music_position + 1)
                    if self.music_offset >= self.music_length:
                        self.music_offset = 0
                        pygame.mixer.music.play(0, self.music_offset)
                        pygame.mixer.music.pause()
                    else:
                        pygame.mixer.music.play(0, self.music_offset)
                if event.key == pygame.K_r: # Restart
                    pygame.mixer.music.rewind()
                    self.music_offset = 0
                    pygame.mixer.music.play(0, self.music_offset)
            if event.type == MUSIC_END: # If the music ends, stop the music
                self.music_offset = 0
                pygame.mixer.music.play(0, self.music_offset)
                pygame.mixer.music.pause()
    
    def draw_controls(self):
        text_surface = self.font.render("[LEFT] Rewind, [RIGHT] Forward, [SPACE] Pause/Resume, r restart", True, (255, 255, 255))
        text_rect = text_surface.get_rect()
        text_rect.topleft = (10, self.height - 20)
        self.screen.blit(text_surface, text_rect)
  
    def draw_minimap(self, x, y, w, h):
        sample_w = w / len(self.wave_data)
        l_y1 = y+h*0.25
        r_y1 = y+h*0.75
        offset = x
        current_pos = pygame.mixer.music.get_pos()
        for l, r in self.wave_data:
            l_y2 = (y+l * h/4) + h*0.25
            r_y2 = (y+r * h/4) + h*0.75
            pygame.draw.line(self.screen, (0, 192, 255), (offset, l_y1), (offset + sample_w, l_y2))
            pygame.draw.line(self.screen, (255, 192, 105), (offset, r_y1), (offset + sample_w, r_y2))
            offset += sample_w
            l_y1 = l_y2
            r_y1 = r_y2

        if current_pos == -1:
            current_pos = 0
        else:
            current_pos = self.music_offset + (current_pos / 1000)  # Convert milliseconds to seconds

        sweeper =  x + (((current_pos) / ((len(self.wave_data)*int(self.samples//(log(self.samples)*100))) / self.samplerate)) * w)
        pygame.draw.line(self.screen, (255, 0, 0), (sweeper, y), (sweeper, y+h),3)



    #https://www.youtube.com/watch?v=oSQTBq1fdTE
    def draw_raw(self, x, y, w, h):
        current_index = (pygame.mixer.music.get_pos()/1000)
        audiowave_size = int(max(AMPLITUDE_SIZE, w))
        interpolation_factor = audiowave_size / w
        if current_index <= 0:
            pygame.draw.line(self.screen, (255, 255, 255), (x, y), (x+w, y),2)
            return
        else:
            current_index = (self.music_offset + current_index)*self.samplerate
        prev_x, prev_y = 0, 0
        for i in range(audiowave_size):
            interpolated_index = int(current_index + i * interpolation_factor)
            if interpolated_index >= len(self.normalized_data):
                break
            l_sum = 0
            count = 0
            for j in range(int(interpolation_factor)):
                if interpolated_index + j < len(self.normalized_data):
                    l, _ = self.normalized_data[int(interpolated_index + j)]
                    l_sum += l
                    count += 1
            if count > 0:
                l = l_sum / count
            else:
                l = 0
            current_x = x + i * (w / audiowave_size)
            current_y = y + (l * h)
            
            if (prev_x, prev_y) != (0, 0):
                pygame.draw.line(self.screen, (203, 102, 163), (prev_x, prev_y), (current_x, current_y))
            prev_x, prev_y = current_x, current_y

    #https://www.youtube.com/watch?v=aQKX3mrDFoY
    def draw_fft(self, x, y, w, h):
        current_index = (pygame.mixer.music.get_pos()/1000)
        current_index = (self.music_offset + current_index)*self.samplerate
        
        left_channel = self.normalized_data[:, 0][int(current_index):int(current_index+FFT_SIZE)]

        # Perform FFT
        if(len(left_channel) < FFT_SIZE):
            return
        
        fft_data = fft(left_channel)
        amplitude = abs(fft_data)
        fft_size = (len(fft_data)//2)-1

        
        # Calculate magnitude spectrum
        self.max_amplitude = max(self.max_amplitude,max(amplitude))
        amplitude = amplitude[:fft_size]/self.max_amplitude
        
        # Draw FFT RAW
        bar_width = 2
        for i in range(min(floor(w/bar_width),(FFT_SIZE//2)-1)): #(FFT_SIZE//2)-1):
            bar_height = min(amplitude[i] * h,h)
            pygame.draw.rect(self.screen, (255, 255, 255), (x + (i * bar_width), y - bar_height, bar_width - 1, bar_height))
            pygame.draw.rect(self.screen, (255, 255, 255), (x + (i * bar_width), y-1, bar_width - 1, 1))
            
    def draw(self):
        self.screen.fill((40, 42, 54))
        
        current_pos = pygame.mixer.music.get_pos()

        self.draw_minimap(self.width/4, 50, self.width/2, 100)
        self.draw_raw(self.width/4,250, self.width/2, 100)
        self.draw_fft(100,550, self.width-200, 200)
        

        
        self.draw_controls()
        pygame.display.flip()

    def play_sound(self):
        pygame.mixer.music.play()

    def run(self):
        self.draw()
        self.play_sound()
        while self.running:
            self.event_loop()
            self.draw()
        pygame.quit()
        

#visualizer = Visualizer("./songs/Geheimnisvolle_Wellenlaengen.wav")
#visualizer = Visualizer("./songs/nicht_zu_laut_abspielen.wav")
visualizer = Visualizer("./songs/bubbles.wav")
visualizer.run()
