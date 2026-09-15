import pygame
import pyaudio
import numpy as np
import math

# --- 1. CONFIGURATION ---
DEVICE_INDEX = 2
RATE = 48000
CHUNK = 1024
CHANNELS = 2

WIDTH, HEIGHT = 1600, 1000
NUM_PLANETS = 200
ROTATION_BASE_SPEED = 0.001

# --- 2. AUDIO SETUP ---
p = pyaudio.PyAudio()
stream = p.open(format=pyaudio.paInt16, channels=CHANNELS, rate=RATE,
                input=True, input_device_index=DEVICE_INDEX, frames_per_buffer=CHUNK)

# --- 3. PYGAME SETUP ---
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

fade_surface = pygame.Surface((WIDTH, HEIGHT))
fade_surface.set_alpha(45)
fade_surface.fill((5, 5, 15))


class CelestialBody:
    def __init__(self, index, is_sun=False):
        self.index = index
        self.is_sun = is_sun
        self.angle = index * 10
        self.radius = 0

        if is_sun:
            self.dist = 0
            self.color = pygame.Color(0, 10, 255)
        else:
            self.dist = 60 + (index * 5)
            self.speed = ROTATION_BASE_SPEED * (1 - (index / (NUM_PLANETS * 1.5)))

            ratio = index / NUM_PLANETS
            r = int(255 * ratio)
            g = int(100 * (1 - ratio))
            b = int(255 * (1 - ratio))
            self.base_color = (r, g, b)

    def update(self, intensity):
        sensitivity = 500 if not self.is_sun else 800
        target_size = (intensity / sensitivity) + (25 if self.is_sun else 2)
        self.radius += (target_size - self.radius) * 0.1
        if not self.is_sun:
            self.angle += self.speed

    def draw(self, surface):
        center_x, center_y = WIDTH // 2, HEIGHT // 2
        brightness = min(100, int(self.radius * 5))

        if self.is_sun:
            for i in range(3, 0, -1):
                glow_r = int(self.radius * (1 + i * 0.4) / 15)
                s = pygame.Surface((glow_r * 2, glow_r * 2), pygame.SRCALPHA)
                color = (50, 200, 255, 150 // i)
                pygame.draw.circle(s, color, (glow_r, glow_r), glow_r)
                surface.blit(s, (center_x - glow_r, center_y - glow_r))
        else:
            x = center_x + self.dist * math.cos(self.angle)
            y = center_y + self.dist * math.sin(self.angle)
            dynamic_color = [min(200, c + brightness) for c in self.base_color]

            # --- THE CHANGE IS HERE ---
            # Added 'width=2' at the end to make them hollow rings
            pygame.draw.circle(surface, dynamic_color, (int(x), int(y)), int(self.radius), width=2)


# Setup
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

    # 1. Update and Draw Planets first
    bins_per_planet = (len(fft_data) - 10) // NUM_PLANETS
    for i, planet in enumerate(planets):
        start = 10 + (i * bins_per_planet)
        end = start + bins_per_planet
        if i < 5:
            intensity = np.mean(fft_data[start:end]) / 2.5
        else:
            intensity = np.mean(fft_data[start:end]) * 1.02 ** (i)
        planet.update(intensity)
        planet.draw(screen)

    # 2. Draw Sun last so it sits on top
    bass = np.mean(fft_data[2:10])
    sun.update(bass)
    sun.draw(screen)

    pygame.display.flip()
    clock.tick(60)

stream.stop_stream()
p.terminate()
pygame.quit()