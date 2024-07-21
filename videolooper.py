import os
import random
import time
import vlc
import RPi.GPIO as GPIO
import threading

# Set the directory for videos
directory = '/home/pi/Videos'

# Initialize list for storing video paths
videos = []

# Create a VLC instance with specific options
vlc_instance = vlc.Instance('--quiet','--file-caching=3000')
#'--avcodec-hw=mmal' maybe helps?

# Populate the videos list with video paths
def getVideos():
    global videos
    videos = [os.path.join(directory, f) for f in os.listdir(directory) if f.lower().endswith('.mp4')]

# Play videos using VLC
def playVideos():
    global videos
    if len(videos) == 0:
        getVideos()
    if len(videos) == 0:
        print("No videos found.")
        return
    random.shuffle(videos)
    for video in videos:
        media = vlc_instance.media_new(video)
        player = vlc_instance.media_player_new()
        player.set_media(media)
        player.play()
        time.sleep(1)  # Wait for the video to start playing
        while player.is_playing():
            time.sleep(1)  # Wait for the video to finish
        player.stop()

# GPIO setup for screen and audio control
def setupGPIO():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(26, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(18, GPIO.OUT)

def turnOnScreen():
    os.system('raspi-gpio set 19 op a5')  # Set GPIO 19 to alternative function for audio
    GPIO.output(18, GPIO.HIGH)  # Turn on the screen backlight

def turnOffScreen():
    os.system('raspi-gpio set 19 ip')  # Set GPIO 19 to input, turning off PWM audio
    GPIO.output(18, GPIO.LOW)  # Turn off the screen backlight

# Function to toggle screen and audio state
def toggleScreen():
    if GPIO.input(18):  # Check if the screen is currently on
        turnOffScreen()
    else:
        turnOnScreen()

# Thread function for controlling screen and audio based on button press
def gpioControl():
    last_state = GPIO.input(26)
    while True:
        current_state = GPIO.input(26)
        if current_state != last_state and current_state == False:
            # Button pressed
            toggleScreen()
        last_state = current_state
        time.sleep(0.1)

# Main function to start threads and play videos
def main():
    setupGPIO()
    # Start the GPIO control thread
    gpio_thread = threading.Thread(target=gpioControl, daemon=True)
    gpio_thread.start()

    # Play videos in the main thread
    playVideos()

if __name__ == "__main__":
    main()
