from PIL import Image
from numpy import average, dot, linalg
import cv2
import json
import os
import progressbar
import coordinate_transform as ct
import math

# Image Similarity
def get_thum(image, size=(64,64), greyscale=False):
    image = image.resize(size, Image.ANTIALIAS)
    if greyscale:
        image = image.convert('L')
    return image
def image_similarity_vectors_via_numpy(image1, image2):
    # image1 = get_thum(image1)
    # image2 = get_thum(image2)   NOTE: get_thum() is always used in this script when a pic is loaded, so this two lined is commented.
    images = [image1, image2]
    vectors = []
    norms = []
    for image in images:
        vector = []
        for pixel_tuple in image.getdata():
            vector.append(average(pixel_tuple))
        vectors.append(vector)
        norms.append(linalg.norm(vector, 2))
    a, b = vectors
    a_norm, b_norm = norms
    res = dot(a / a_norm, b / b_norm)
    return res

# Test Code
# count = 0
# for i in range(0,25):
	# image1 = Image.open('20190724_20190724090949_20190724204645_091102_crop//'+str(i)+'.jpg')
	# image2 = Image.open('20190724_20190724090949_20190724204645_091102_crop//'+str(i+1)+'.jpg')
	# image2 = Image.open('20190724_20190724090949_20190724204645_091102_crop//2929.jpg')
	# cosin = image_similarity_vectors_via_numpy(image1, image2)
	# print(str(i)+'-'+str(i+1)+': '+str(cosin))
	# print(str(i)+': '+str(cosin))
	# if cosin >= 0.8:
		# count += 1
	# print(count/(i+1))

# Global Variable
cropImgaePath = '//home//ssongad//Video//20190724_20190724090949_20190724204645_091102//20190724_20190724090949_20190724204645_091102_crop'
activeDuration = 2 # unit == second
imageSimilarThreshold = 0.8
peopleSimilarThreshold = 0.8
activePeople = []

class MyTime:
	
	def __init__(self,h,m,s,ms):
		self.h = h
		self.m = m
		self.s = s
		self.ms = ms
	
	@classmethod
	def fromSeconds(cls,s):
		ms = s - int(s)
		s_ = int(s) % 60
		temp = int(int(s) / 60)
		m = temp % 60
		h = int(temp / 60) % 24
		return MyTime(h,m,s_,ms)
		
	
	def asSeconds(self):
		return self.h*3600+self.m*60+self.s+self.ms
	
	def __sub__(self, anotherTime):
		return self.asSeconds() - anotherTime.asSeconds()
	
	def __ge__(self, anotherTime):
		return self.asSeconds() >= anotherTime.asSeconds()
	
	def __le__(self, anotherTime):
		return self.asSeconds() <= anotherTime.asSeconds()
	
	def __lt__(self, anotherTime):
		return not self >= anotherTime
	
	def __gt__(self, anotherTime):
		return not self <= anotherTime
	
	def __str__(self):
		return str(self.h)+':'+str(self.m)+':'+str(self.s)
	
class Person:
	
	def __init__(self, id, dicts):
		self.id = id
		self.dicts = []
		self.images = []
		for dict in dicts:
			self.addDict(dict)
		
	def addDict(self, dict):
		dict['id'] = self.id
		self.dicts.append(dict)
		self.images.append(get_thum(Image.open(cropImgaePath+'//'+str(dict['index'])+'.jpg')))
		
	
	def lastCoor(self):
		dict = self.dicts[-1]
		return [dict['x'],dict['y']]
	
	def lastTime(self):
		dict = self.dicts[-1]
		return MyTime(dict['h'],dict['m'],dict['s'],dict['ms'])
	
	def image_similarity(self,index):
		theImage = get_thum(Image.open(cropImgaePath+'//'+str(index)+'.jpg'))
		total = len(self.images)
		
		hit_count = 0
		total_count = 0
		for image in self.images[::math.ceil(total/5)]:
			result = image_similarity_vectors_via_numpy(theImage, image)
			if result >= imageSimilarThreshold:
				hit_count += 1
			elif result <= 0.7:
				return 0
			total_count += 1
		return hit_count/total_count
	
	def isActive(self, currentTime):
		return True if currentTime - self.lastTime() <= activeDuration else False
		
def removeUnactivePeople(currentTime):
	for i, person in enumerate(activePeople):
		if not person.isActive(currentTime):
			del activePeople[i]

def processJson(jsonPath):
	f = open(jsonPath,'r')
	dicts = json.load(f)
	f.close()
	
	# Set up progress bar
	print('Processing JSON Now')
	total = len(dicts)
	b = progressbar.ProgressBar(max_value=total).start()
	
	id = 0
	b_count = 0
	for dict in dicts:
		try:
			Image.open(cropImgaePath+'//'+str(dict['index'])+'.jpg')
		except:
			continue
		else:
			currentTime = MyTime(dict['h'],dict['m'],dict['s'],dict['ms'])
			currentCoor = ct.Point(dict['x'],dict['y'])
		
			if len(activePeople) == 0:
				p = Person(id, [dict])
				activePeople.append(p)
				dict['id'] = id # Check if this statement can be removed
				id += 1
			else:
				waitlist = []
				for i, person in enumerate(activePeople):
					similarity = person.image_similarity(dict['index'])
					
					if similarity >= peopleSimilarThreshold:
						waitlist.append(i)
					
				if len(waitlist) == 0:
					p = Person(id, [dict])
					activePeople.append(p)
					dict['id'] = id # Check if this statement can be removed
					id += 1
				elif len(waitlist) == 1:
					person = activePeople[waitlist[0]]
					person.addDict(dict)
					dict['id'] = person.id # Check if this statement can be removed
				else:
					distances = []
					for j in waitlist:
						p = ct.Point.from_array(activePeople[j].lastCoor())
						distances.append(p.distance(currentCoor))
					minD = min(distances)
					person = activePeople[waitlist[distances.index(minD)]]
					person.addDict(dict)
					dict['id'] = person.id # Check if this statement can be removed
						
			removeUnactivePeople(currentTime)
			b_count += 1
			if b_count <= total:
				b.update(b_count)
	
	b.finish()
	f = open(os.path.dirname(jsonPath)+'//final.json','w')
	json.dump(dicts,f)
	f.close()
			
if __name__ == '__main__':
	
	processJson('//home//ssongad//Video//20190724_20190724090949_20190724204645_091102//20190724_20190724090949_20190724204645_091102_trans.json')
			
			
			
			
			
			
			
			