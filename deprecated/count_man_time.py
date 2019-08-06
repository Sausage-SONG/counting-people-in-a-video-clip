import face_recognition as fr
import os
from PIL import Image
import cv2

# Conversion between face_encoding and string
def encoding2str(encoding):
	result = ''
	for i in encoding:
		result += str(i)+'\t'
	return result
def str2encoding(string):
	result = []
	numbers = string.split('\t',127)
	for number in numbers:
		result.append(float(number))
	return result
	
# Person Class
class Person:
	locations = []
	encodings = []
	
	def __init__(self, location, encoding):
		self.encodings.append(encoding)
		self.locations.append(location)
	
	def isThis(self, encoding):
		results = fr.compare_faces(self.encodings, encoding, 0.6)		# NEED IMPROVEMENT
		count = 0
		for result in results:
			count += 1 if result else 0
		return True if count / len(results) >= 0.8 else False			# NEED IMPROVEMENT
		
	def add(self, location, encoding):
		self.encodings.append(encoding)
		self.locations.append(location)
		
	def absent(self):
		self.locations.append(None)
		
	def count(self):
		holes = []
		active = False
		hole = [0,0]
		for i, l in enumerate(self.locations):
			if l == None:
				if active:
					continue
				else:
					active = True
					hole[0] = i
			else:
				if active:
					active = False
					hole[1] = i - 1
					holes.append(hole)
				else:
					continue
		return len(holes)+1					# NEED IMPROVEMENT
			
				
				

# Video Processing
def getScreenshot(videoPath, timeF = 30, imagePath = './/screenshot'):
	vc = cv2.VideoCapture(videoPath)
	c = 0
	i = 0
	
	if vc.isOpened():
		rval, frame = vc.read()
	else:
		rval = False
	
	if os.path.exists(imagePath):
		os.system('rm -r '+imagePath)
	os.system('mkdir '+imagePath)
		
	while rval:
		rval, frame = vc.read()
		if c % timeF == 0:
			cv2.imwrite(imagePath+'//'+str(i)+'.jpg', frame)
			i += 1
		c += 1
		cv2.waitKey(1)
	vc.release()
def processScreenshot(people, imagePath = './/screenshot'):
	names = os.listdir(imagePath)
	names.sort()
	for name in names:
		found = [False,]*len(people)
		image = fr.load_image_file(imagePath+'//'+name)
		face_locations = fr.face_locations(image)
		
		if len(face_locations) == 0:
			for person in people:
				person.absent()
		for location in face_locations:
			encodings = fr.face_encodings(image, [location], 1)			# NEED IMPROVEMENT
			if len(encodings) == 0:
				continue
			encoding = encodings[0]
			
			foundThisOne = False
			for i, person in enumerate(people):
				if person.isThis(encoding):
					person.add(location, encoding)
					found[i] = True
					foundThisOne = True
					break
			if not foundThisOne:
				people.append(Person(location, encoding))
	
	for i, r in enumerate(found):
		if not r:
			people[i].absent()

# Global Variables
people = []

# Counting Function
def count(videoPath, timeF = 30, imagePath = './/screenshot'):
	getScreenshot(videoPath, timeF, imagePath)
	processScreenshot(people, imagePath = './/screenshot')
	
	result = 0
	for person in people:
		result += person.count()
	return result
	

# Main
# print(count('.//1.mp4'))  -- for example
