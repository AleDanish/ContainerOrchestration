import time
import subprocess

def download_image(name_image):
    cmd = "docker pull " + name_image
    proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
    for line in iter(proc.stdout.readline,''):
        print(line)
        break

image = "alez/test-app-raspi:3"
startBaseImage = time.time()
download_image(image)
timeBaseImage = time.time() - startBaseImage
print("Total time to download " + image + " is " + str(timeBaseImage) + " s \n")

image = "alez/mongo-raspi:3"
startBaseImage = time.time()
download_image(image)
timeBaseImage = time.time() - startBaseImage
print("Total time to download " + image + " is " + str(timeBaseImage) + " s \n")

image = "alez/mosquitto-raspi"
startBaseImage = time.time()
download_image(image)
timeBaseImage = time.time() - startBaseImage
print("Total time to download " + image + " is " + str(timeBaseImage) + " s \n")
