# tracking-people-in-surveillance-videos
This is the HKUST UROP project: **AI meets Big Data** (2019 Summer) carried out by [SONG Sizhe](https://github.com/Sausage-SONG) and supervised by Prof. Shueng-Han Gary Chan. This project focuses on tracking people in the surveillance videos.

## Usage
This project uses [Yolo](https://pjreddie.com/darknet/yolo/) for people detecting, so you need to install Yolo first.  

```shell
git clone https://github.com/pjreddie/darknet
cd darknet
make
``` 

Clone Yolo and compile using commands above. You may need to modify the `<your directory>/darknet/Makefile` to enable a GPU or OpenCV if available on your machine. At the very beginning, set the value to 1 to turn on a tool, and remember to re-compile.  

A more detailed instruction can be found on [Yolo official page](https://pjreddie.com/darknet/yolo/).  

After Yolo is installed, copy the scripts in this repo including `process_video.py`, `coordinate_transform.py`, `id_process.py` to Yolo python scripts' folder `<your directory>/darknet/python`.

## I'm still working on this md.

## Report
You can find the report of this project [here](https://github.com/Sausage-SONG/tracking-people-in-surveillance-videos/blob/master/UROP1100X_SONG%20Sizhe.pdf).  

**Warning: Carefully choose your directory, or you may accidentally DELETE your own files. Please always read the code if you are not sure.**
