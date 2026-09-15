import pygame
import pyaudio
import numpy as np
import math

# --- 1. CONFIGURATION ---
DEVICE_INDEX = 2  # Set to your CABLE Output index
RATE = 48000  # Match your headphone/cable sample rate
CHUNK = 1024
CHANNELS = 2

WIDTH, HEIGHT = 900, 900
NUM_PLANETS = 70
ROTATION_BASE_SPEED = 0.015

# --- 2. AUDIO SETUP ---
p = pyaudio.PyAudio()
stream = p.open(format=pyaudio.paInt16, channels=CHANNELS, rate=RATE,
                input=True, input_device_index=DEVICE_INDEX, frames_per_buffer=CHUNK)

# --- 3. PYGAME SETUP ---
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

# Motion blur surface
fade_surface = pygame.Surface((WIDTH, HEIGHT))
fade_surface.set_alpha(45)
fade_surface.fill((5, 5, 15))


class CelestialBody:
    def __init__(self, index, is_sun=False):
        self.index = index
        self.is_sun = is_sun
        self.angle = index * 10  # Stagger the starting positions
        self.radius = 0

        if is_sun:
            self.dist = 0
            self.color = pygame.Color(0, 10, 255)  # Deep Blue for Bass Sun
        else:
            self.dist = 60 + (index * 20) #distance
            self.speed = ROTATION_BASE_SPEED * (1 - (index / (NUM_PLANETS * 1.5)))

            # --- COLOR MAPPING (Blue to Red) ---
            # i/NUM_PLANETS gives us a value from 0 to 1
            ratio = index / NUM_PLANETS
            r = int(255 * ratio)  # Red increases as we go out
            g = int(100 * (1 - ratio))  # Some green in the middle for smoothness
            b = int(255 * (1 - ratio))  # Blue decreases as we go out
            self.base_color = (r, g, b)

    def update(self, intensity):
        # Smoothing the size
        # Planets get more 'sensitive' as they move out (intensity / 400 vs 800)
        sensitivity = 500 if not self.is_sun else 800
        target_size = (intensity / sensitivity) + (25 if self.is_sun else 2)

        self.radius += (target_size - self.radius) * 0.1

        if not self.is_sun:
            self.angle += self.speed

    def draw(self, surface):
        center_x, center_y = WIDTH // 2, HEIGHT // 2

        # Color brightness react to intensity
        # We cap it at 255 to avoid errors
        brightness = min(100, int(self.radius * 5))

        if self.is_sun:
            # Sun Glow Effect
            for i in range(3, 0, -1):
                glow_r = int(self.radius * (1 + i * 0.4)/5)
                s = pygame.Surface((glow_r * 2, glow_r * 2), pygame.SRCALPHA)
                # Pulse the blue color brightness
                color = (0, 150, 255, 150 // i)
                pygame.draw.circle(s, color, (glow_r, glow_r), glow_r)
                surface.blit(s, (center_x - glow_r, center_y - glow_r))
        else:
            # Orbiting Planets
            x = center_x + self.dist * math.cos(self.angle)
            y = center_y + self.dist * math.sin(self.angle)

            # Dynamic Color: Flashes brighter when the frequency hits
            dynamic_color = [min(200, c + brightness) for c in self.base_color]

            pygame.draw.circle(surface, dynamic_color, (int(x), int(y)), int(self.radius))


# Setup bodies
sun = CelestialBody(0, is_sun=True)
planets = [CelestialBody(i + 1) for i in range(NUM_PLANETS)]

running = True
while running:
    screen.blit(fade_surface, (0, 0))
    for event in pygame.event.get():
        if event.type == pygame.QUIT: running = False

    try:
        raw_data = stream.read(CHUNK, exception_on_overflow=False)
        samples = np.frombuffer(raw_data, dtype=np.int16)
        fft_data = np.abs(np.fft.fft(samples))[:CHUNK // 2]
    except:
        fft_data = np.zeros(CHUNK // 2)

    # 1. Update Sun (Bass: indices 2 to 10)
    bass = np.mean(fft_data[2:10])
    sun.update(bass)
    sun.draw(screen)

    # 2. Update Planets (The rest of the spectrum)
    bins_per_planet = (len(fft_data) - 10) // NUM_PLANETS
    for i, planet in enumerate(planets):
        start = 10 + (i * bins_per_planet)
        end = start + bins_per_planet
        if i==0 or i==1 or i==2 or i==3 or i==4:
            intensity = np.mean(fft_data[start:end])/4
        else:
            intensity = np.mean(fft_data[start:end]) * 1.01 ** (i)
        planet.update(intensity)
        planet.draw(screen)

    pygame.display.flip()
    clock.tick(60)

stream.stop_stream()
p.terminate()
pygame.quit()