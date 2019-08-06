from ctypes import *
from PIL import Image
import math
import random
import cv2
import os
import progressbar
import time
import json

def sample(probs):
    s = sum(probs)
    probs = [a/s for a in probs]
    r = random.uniform(0, 1)
    for i in range(len(probs)):
        r = r - probs[i]
        if r <= 0:
            return i
    return len(probs)-1

def c_array(ctype, values):
    arr = (ctype*len(values))()
    arr[:] = values
    return arr

class BOX(Structure):
    _fields_ = [("x", c_float),
                ("y", c_float),
                ("w", c_float),
                ("h", c_float)]

class DETECTION(Structure):
    _fields_ = [("bbox", BOX),
                ("classes", c_int),
                ("prob", POINTER(c_float)),
                ("mask", POINTER(c_float)),
                ("objectness", c_float),
                ("sort_class", c_int)]


class IMAGE(Structure):
    _fields_ = [("w", c_int),
                ("h", c_int),
                ("c", c_int),
                ("data", POINTER(c_float))]

class METADATA(Structure):
    _fields_ = [("classes", c_int),
                ("names", POINTER(c_char_p))]

#lib = CDLL("/home/pjreddie/documents/darknet/libdarknet.so", RTLD_GLOBAL)
lib = CDLL("libdarknet.so", RTLD_GLOBAL)
lib.network_width.argtypes = [c_void_p]
lib.network_width.restype = c_int
lib.network_height.argtypes = [c_void_p]
lib.network_height.restype = c_int

predict = lib.network_predict
predict.argtypes = [c_void_p, POINTER(c_float)]
predict.restype = POINTER(c_float)

set_gpu = lib.cuda_set_device
set_gpu.argtypes = [c_int]

make_image = lib.make_image
make_image.argtypes = [c_int, c_int, c_int]
make_image.restype = IMAGE

get_network_boxes = lib.get_network_boxes
get_network_boxes.argtypes = [c_void_p, c_int, c_int, c_float, c_float, POINTER(c_int), c_int, POINTER(c_int)]
get_network_boxes.restype = POINTER(DETECTION)

make_network_boxes = lib.make_network_boxes
make_network_boxes.argtypes = [c_void_p]
make_network_boxes.restype = POINTER(DETECTION)

free_detections = lib.free_detections
free_detections.argtypes = [POINTER(DETECTION), c_int]

free_ptrs = lib.free_ptrs
free_ptrs.argtypes = [POINTER(c_void_p), c_int]

network_predict = lib.network_predict
network_predict.argtypes = [c_void_p, POINTER(c_float)]

reset_rnn = lib.reset_rnn
reset_rnn.argtypes = [c_void_p]

load_net = lib.load_network
load_net.argtypes = [c_char_p, c_char_p, c_int]
load_net.restype = c_void_p

do_nms_obj = lib.do_nms_obj
do_nms_obj.argtypes = [POINTER(DETECTION), c_int, c_int, c_float]

do_nms_sort = lib.do_nms_sort
do_nms_sort.argtypes = [POINTER(DETECTION), c_int, c_int, c_float]

free_image = lib.free_image
free_image.argtypes = [IMAGE]

letterbox_image = lib.letterbox_image
letterbox_image.argtypes = [IMAGE, c_int, c_int]
letterbox_image.restype = IMAGE

load_meta = lib.get_metadata
lib.get_metadata.argtypes = [c_char_p]
lib.get_metadata.restype = METADATA

load_image = lib.load_image_color
load_image.argtypes = [c_char_p, c_int, c_int]
load_image.restype = IMAGE

rgbgr_image = lib.rgbgr_image
rgbgr_image.argtypes = [IMAGE]

predict_image = lib.network_predict_image
predict_image.argtypes = [c_void_p, IMAGE]
predict_image.restype = POINTER(c_float)

# Yolo Function
def classify(net, meta, im):
    out = predict_image(net, im)
    res = []
    for i in range(meta.classes):
        res.append((meta.names[i], out[i]))
    res = sorted(res, key=lambda x: -x[1])
    return res
def detect(net, meta, image, thresh=.5, hier_thresh=.5, nms=.45):
    im = load_image(image, 0, 0)
    if im.w == 0:
	    return []
    num = c_int(0)
    pnum = pointer(num)
    predict_image(net, im)
    dets = get_network_boxes(net, im.w, im.h, thresh, hier_thresh, None, 0, pnum)
    num = pnum[0]
    if (nms): do_nms_obj(dets, num, meta.classes, nms);

    res = []
    for j in range(num):
        for i in range(meta.classes):
            if dets[j].prob[i] > 0:
                b = dets[j].bbox
                res.append((meta.names[i], dets[j].prob[i], (b.x, b.y, b.w, b.h)))
    res = sorted(res, key=lambda x: -x[1])
    free_image(im)
    free_detections(dets, num)
    return res

def getFrames(videoPath, framePerSec = 2, rotate = False, interval = None):
	# Reset output frame directory
	print('Geting Frames Now')
	imagePath = os.path.splitext(videoPath)[0]
	if os.path.exists(imagePath):
		os.system('rm -r '+imagePath)
	os.system('mkdir '+imagePath)
	
	# Open the video
	vc = cv2.VideoCapture(videoPath)
	
	# FPS info && frame frequency
	fps = int(round(vc.get(cv2.CAP_PROP_FPS)))
	timeF = fps/framePerSec
	
	# Interval setting
	totalFrame = int(vc.get(cv2.CAP_PROP_FRAME_COUNT))
	if type(interval) == type(None):
		interval = (0,totalFrame)
	else:
		start = interval[0]*3600+interval[1]*60+interval[2]
		end = interval[3]*3600+interval[4]*60+interval[5]
		interval = (start*fps,end*fps)
	
	# Set Video
	if type(interval) != type(None):
		vc.set(cv2.CAP_PROP_POS_FRAMES,interval[0])
	
	# Set up progress bar
		total = interval[1]-interval[0]
	else:
		total = totalFrame
	bar = progressbar.ProgressBar(max_value=total).start()
	
	# Check if the video is successfully opened
	if vc.isOpened():
		rval, frame = vc.read()
	else:
		rval = False
	
	# Counter
	frame_i = 0
	file_i = 0
	
	# Loop to read and write the frames
	while rval:
		rval, frame = vc.read()
		if frame_i > total:
			break;
		if frame_i % timeF == 0:
			if rotate:
				im = Image.fromarray(frame[:, :, ::-1])
				im_rotate = im.rotate(180)
				im_rotate.save(imagePath+'//'+str(file_i)+'.jpg')
			else:
				cv2.imwrite(imagePath+'//'+str(file_i)+'.jpg', frame)
			bar.update(frame_i)
			file_i += 1
		frame_i += 1
		cv2.waitKey(1)
	
	bar.finish()
	vc.release()
	
def combineFrames(fps, size, imagePath, outputPath = ' '):
	# Default directory
	if outputPath == ' ':
		outputPath = imagePath + '.avi'
	if os.path.exists(outputPath):
		os.system('rm '+outputPath)
	
	print('Combining Frames Now')
	# Set up progress bar
	total = len(os.listdir(imagePath))
	bar = progressbar.ProgressBar(max_value=total).start()
	
	# Set up video writer
	fourcc = cv2.VideoWriter_fourcc(*'XVID')
	vw = cv2.VideoWriter(outputPath,fourcc,fps,size)
	
	# Loop to read and write frames
	errorList = ''
	i = 0
	while(os.path.exists(imagePath+'//'+str(i)+'.jpg')):
		try:
			frame = cv2.imread(imagePath+'//'+str(i)+'.jpg')
		except:
			errorList += (str(i)+'.jpg'+'\n')
			i += 1
			continue
		
		vw.write(frame)
		if i < total:
			bar.update(i)
		i += 1
	
	# Release bar and video
	bar.finish()
	vw.release()
	
	# Print failed frames list
	if errorList != '':
		print('Frames below are not added:\n' + errorList)

def outputVideo(videoPath, framePerSec = 5, rotate = False, interval = None):
	# Get frames
	getFrames(videoPath, framePerSec, rotate, interval)
	framePath = os.path.splitext(videoPath)[0]
	
	# Reset output directory
	newFramePath = os.path.splitext(videoPath)[0] + '_out'
	if os.path.exists(newFramePath):
		os.system('rm -r '+newFramePath)
	os.system('mkdir '+newFramePath)
	
	# Yolo
	net = load_net(b"cfg/yolov3.cfg", b"yolov3.weights", 0)
	meta = load_meta(b"cfg/coco.data")
	
	# Set up progress bar
	print('Processing Frames Now')
	total = len(os.listdir(framePath))
	bar = progressbar.ProgressBar(max_value=total).start()
	
	# Loop to read and process frames
	errorList = ''
	in_i = 0
	out_i = 0
	while(os.path.exists(framePath+'//'+str(in_i)+'.jpg')):
		imagePath = framePath+'//'+str(in_i)+'.jpg'
		fr = cv2.imread(imagePath)
		if type(fr) == type(None):
			errorList += (str(in_i)+'.jpg'+'\n')
			in_i += 1
			continue
		r = detect(net, meta, str.encode(imagePath))
		
		for obj in r:
			if obj[0] == b'person':
				cv2.rectangle(fr,(int(obj[2][0]-0.5*obj[2][2]),int(obj[2][1]-0.5*obj[2][3])),(int(obj[2][0]+0.5*obj[2][2]),int(obj[2][1]+0.5*obj[2][3])),(0,0,255),3)
		cv2.imwrite(newFramePath+'//'+str(out_i)+'.jpg', fr)
		
		if in_i < total:
			bar.update(in_i)
		in_i += 1
		out_i += 1
	bar.finish()
	if errorList != '':
		print('Frames below are not processed:\n'+errorList)
	
	# Combine frames to video output
	vc = cv2.VideoCapture(videoPath)
	fps = int(round(vc.get(cv2.CAP_PROP_FPS)))
	size = (int(vc.get(cv2.CAP_PROP_FRAME_WIDTH)),int(vc.get(cv2.CAP_PROP_FRAME_HEIGHT)))
	vc.release()
	combineFrames(fps,size,newFramePath)

def addTime(h,m,s,s_):
	ms = s_ - int(s_)
	
	temp = s + int(s_)
	s = temp % 60
	s_ = int(temp / 60)
	
	temp = m + s_
	m = temp % 60
	s_ = int(temp / 60)
	
	h = (h+s_) % 24
	return (h,m,s,ms)
	
def outputData(videoPath, startTime, framePerSec = 5, rotate = False, interval = None):
	# Time Calculation
	vc = cv2.VideoCapture(videoPath)
	fps = int(round(vc.get(cv2.CAP_PROP_FPS)))
	vc.release()
	
	# Get frames
	# getFrames(videoPath, framePerSec, rotate, interval)
	
	# Yolo
	net = load_net(b"cfg/yolov3.cfg", b"yolov3.weights", 0)
	meta = load_meta(b"cfg/coco.data")
	
	# Set up progress bar
	print('Processing Frames Now')
	dirPath = os.path.splitext(videoPath)[0]
	total = len(os.listdir(dirPath))
	bar = progressbar.ProgressBar(max_value=total).start()
	
	# Set up crop pic directory
	cropPath = dirPath + '_crop'
	if os.path.exists(cropPath):
		os.system('rm -r '+cropPath)
	os.system('mkdir '+cropPath)
	
	# Loop
	i = 0
	index = 0
	dicts = []
	while True:
		framePath = dirPath + '//' + str(i) + '.jpg'
		if not os.path.exists(framePath):
			break;
		
		r = detect(net, meta, str.encode(framePath))
		
		theTime = addTime(startTime[0], startTime[1], startTime[2], (i*framePerSec+1)/fps)
		theDict = {'h':theTime[0],'m':theTime[1],'s':theTime[2],'ms':theTime[3],'index':0,'id':None,'x':0,'y':0}
		
		for obj in r:
			if obj[0] == b'person':
				theDict['index'] = index
				theDict['x'] = obj[2][0]
				theDict['y'] = obj[2][1]
				dicts.append(theDict)
								
				img = cv2.imread(framePath)
				cropped = img[int(obj[2][1]-obj[2][3]/2):int(obj[2][1]+obj[2][3]/2), int(obj[2][0]-obj[2][2]/2):int(obj[2][0]+obj[2][2]/2)]
				cv2.imwrite(cropPath+'//'+str(index)+'.jpg', cropped)
				index += 1
		
		if i < total:
			bar.update(i)
		i += 1
	
	bar.finish()
	# Write JSON
	f = open(dirPath+'.json','w')
	json.dump(dicts, f)
	f.close()

# def findCoor(imagePath,start,end):
	# # Yolo
	# net = load_net(b"cfg/yolov3.cfg", b"yolov3.weights", 0)
	# meta = load_meta(b"cfg/coco.data")
	
	# dots = []
	# for i in range(start,end+1):
		# r = detect(net, meta, str.encode(imagePath+'//'+str(i)+'.jpg'))
	
		# for obj in r:
			# if obj[0] == b'person':
				# dots.append([i,obj[2][0],obj[2][1]])
	
	# for dot in dots:
		# print(dot)
	
    
if __name__ == "__main__":
    #net = load_net("cfg/densenet201.cfg", "/home/pjreddie/trained/densenet201.weights", 0)
    #im = load_image("data/wolf.jpg", 0, 0)
    #meta = load_meta("cfg/imagenet1k.data")
    #r = classify(net, meta, im)
    #print r[:10]
	
	# net = load_net(b"cfg/yolov3.cfg", b"yolov3.weights", 0)
	# meta = load_meta(b"cfg/coco.data")
	# r = detect(net, meta, b"data/person.jpg")
	# print(r)
	# for each in r:
		# if each[0] == b'person':
			# print("DONE")
		# else:
			# print(each[0])
	
	# outputVideo('//home//ssongad//Video//20190724_20190724090949_20190724204645_091102//20190724_20190724090949_20190724204645_091102.mp4',rotate = True, interval = (4,12,0,4,29,10))
	# outputData('//home//ssongad//Video//20190724_20190724090949_20190724204645_091102//20190724_20190724090949_20190724204645_091102.mp4',(13,21,50),rotate = True, interval = (4,12,0,4,29,10))
	outputData('//home//ssongad//Video//20190724_20190724090949_20190724204645_091102//20190724_20190724090949_20190724204645_091102.mp4',(13,21,50),rotate = True)
