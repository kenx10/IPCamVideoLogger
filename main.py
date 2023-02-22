import glob
import json
import os
import threading
import time

import cv2
import requests

requests.adapters.DEFAULT_RETRIES = 5


def upload_file(upload_url, file_path, delete=False):
    with open(file_path, 'rb') as f:
        try:
            test_res = requests.post(upload_url, files={"video_file": f})

            if test_res.ok:
                print(" File %s uploaded successfully ! " % test_res.text)
            else:
                print(" Error Upload file %s ! " % test_res.text)
        except requests.exceptions.ConnectionError:
            print(" Can't connect ")

        f.close()

    if delete:
        os.remove(file_path)


def video_cam(cam_name, rtsp_url, upload_base='http://localhost:8080'):
    out_file_pattern = 'videos/' + cam_name + '-%s.avi'
    cap = cv2.VideoCapture(rtsp_url)

    # Get current width of frame
    width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)  # float
    height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)  # float

    # Define the codec and create VideoWriter object
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')

    out_file = out_file_pattern % time.time()
    out = cv2.VideoWriter(out_file, fourcc, 20.0, (int(width), int(height)))

    while cap.isOpened():
        try:
            ret, frame = cap.read()

            if ret:
                # Saves for video
                out.write(frame)

                # Display the resulting frame
                # cv2.imshow('frame', frame)
            else:
                break

            if 4_096_000 < os.path.getsize(out_file):
                out.release()
                upload_file(upload_url='%s/upload/cam/%s' % (upload_base, cam_name),
                            file_path=out_file,
                            delete=True)

                out_file = out_file_pattern % time.time()
                out = cv2.VideoWriter(out_file, fourcc, 20.0, (int(width), int(height)))

        except Exception as e:
            print(e)

    cap.release()
    out.release()
    cv2.destroyAllWindows()


if __name__ == '__main__':
    with open('config.json', 'r') as conf:
        config = json.load(conf)

        upload_base = config['upload_base']
        cams = config['cams']

        if not os.path.exists('videos'):
            os.mkdir('videos', 0o755)

        files = glob.glob('videos/*')
        for f in files:
            os.remove(f)

        for key in cams:
            x = threading.Thread(target=video_cam, args=(key, cams[key], upload_base))
            x.start()
            x.join()
