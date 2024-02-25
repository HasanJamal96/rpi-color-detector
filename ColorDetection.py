import cv2, os, signal
from multiprocessing import Process

AUDIO_FILE_LOC = '/home/pi/Desktop/sample.wav'

lastColorDetected    = None
currentColorDetected = None

audioProcess = None

RED   = 0
GREEN = 1


cap = cv2.VideoCapture(0, cv2.CAP_V4L)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)



def _play():
    os.system('aplay --device=hw:1,0 ' + AUDIO_FILE_LOC)


def _stop():
    global audioProcess
    try:
        os.system('sudo pkill -f aplay')
        os.kill(audioProcess.pid, signal.SIGTERM)
    except:
        pass
    audioProcess = None
    print('Audio stopped')


def playAudio() -> None:
    global audioProcess
    if(not audioProcess):
        audioProcess = Process(target=_play)
        audioProcess.start()


def stopAudio() -> None:
    global audioProcess
    if(audioProcess):
        _stop()

try:
    while True:
        if(audioProcess):
            if(not audioProcess.is_alive()):
                _stop()
        _, frame = cap.read()
        hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        height, width, _ = frame.shape

        cx = int(width / 2)
        cy = int(height / 2)

        pixel_center = hsv_frame[cy, cx]
        hue_value = pixel_center[0]

        currentColorDetected = None
        color = 'Undefined'
        if (hue_value < 30 or hue_value > 350 or (hue_value > 170 and hue_value < 175)):
            currentColorDetected = RED
            color = 'RED'
            if(currentColorDetected != lastColorDetected):
                lastColorDetected = currentColorDetected
                playAudio()
        #elif (hue_value < 72 and hue_value > 30):
        elif (hue_value < 87 and hue_value > 76):
            currentColorDetected = GREEN
            color = 'Green'
            if(currentColorDetected != lastColorDetected):
                lastColorDetected = currentColorDetected
                playAudio()
        else:
            currentColorDetected = None


        pixel_center_bgr = frame[cy, cx]
        b, g, r = int(pixel_center_bgr[0]), int(pixel_center_bgr[1]), int(pixel_center_bgr[2])

        cv2.rectangle(frame, (cx - 220, 10), (cx + 200, 120), (255, 255, 255), -1)
        cv2.putText(frame, color, (cx - 200, 100), 0, 3, (b, g, r), 5)
        cv2.circle(frame, (cx, cy), 5, (25, 25, 25), 3)

        cv2.imshow("Frame", frame)
        key = cv2.waitKey(1)
        if key == 27:
            break

    cap.release()
    cv2.destroyAllWindows()
    _stop()

except Exception as e:
    print('Error -> ', e)
    cap.release()
    cv2.destroyAllWindows()
    _stop()
