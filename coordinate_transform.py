import json
import math
import os
import progressbar
# import turtle (turtle is for test only. So are the codes below about turtle.)

class Point:
	
	def __init__(self, x = 0, y = 0):
		self.x = x
		self.y = y
		
	@classmethod
	def from_array(cls, arr):
		return Point(arr[0],arr[1])
	
	def __str__(self):
		return '('+str(self.x)+','+str(self.y)+')'
		
	def slope(self, another_point):
		y = another_point.y - self.y
		x = another_point.x - self.x
		return None if x == 0 else y/x
	
	def distance(self, another_point):
		return math.sqrt((self.x-another_point.x)**2 + (self.y-another_point.y)**2)
		
	def isInside(self, obj, boundryIncluded = False):
		return obj.hasPointInside(self, boundryIncluded)
		
class Line:

	def __init__(self, k = 0, d = 0):
		self.k = k
		self.d = d
		
	@classmethod	
	def from_points(cls, point_a, point_b):
		k = point_a.slope(point_b)
		if type(k) == type(None):
			d = point_a.x
		else:
			d = point_a.y - k * point_a.x
		return Line(k, d)
	
	def __str__(self):
		if type(self.k) == type(None):
			result = 'x = ' + str(self.d)
		else:
			result = 'y = '
			if self.k != 0:
				result += str(self.k)+'x'
			if self.d != 0:
				result += ' + '+str(self.d)
		return result
	
	def __eq__(self,another_line):
		if type(self.k) == type(None) or type(another_line.k) == type(None):
			if type(self.k) == type(None) and type(another_line.k) == type(None):
				return self.d == another_line.d
			return False
		elif self.k == another_line.k and self.d == another_line.d:
			return True
		return False
	
	def is_parallel(self, another_line):
		if type(self.k) == type(None) or type(another_line.k) == type(None):
			if type(self.k) == type(None) and type(another_line.k) == type(None):
				return True if not self.d == another_line.d else False
			return False
		elif self.k == another_line.k and not self.d == another_line.d:
			return True
		return False
		
	def intersect(self, another_line):
		if self.is_parallel(another_line) or self == another_line:
			print('---ERROR: THE LINES DO NOT INTERSECT WITH EACH OTHER---')
			return None
		if type(self.k) == type(None):
			return Point(self.d, another_line.k * self.d + another_line.d)
		elif type(another_line.k) == type(None):
			return Point(another_line.d, self.k * another_line.d + self.d)
		else:
			x = (another_line.d - self.d) / (self.k - another_line.k)
			y = self.k * x + self.d
			return Point(x, y)

class Triangle:
	
	def __init__(self,point1,point2,point3):
		if Line(point1,point2) == Line(point2,point3):
			self.points = None
			print('---ERROR: TRY TO BUILD A TRIANGLE WITH POINTS AT THE SAME LINE---')
		else:
			self.points = [point1,point2,point3]
	
	@classmethod
	def from_array(cls, points):
		return cls(points[0],points[1],points[2])
	
	def hasPointInside(self, thePoint, boundryIncluded = False):
		x1 = self.points[1].x - self.points[0].x
		y1 = self.points[1].y - self.points[0].y
		
		x2 = self.points[2].x - self.points[0].x
		y2 = self.points[2].y - self.points[0].y
		
		x3 = thePoint.x - self.points[0].x
		y3 = thePoint.y - self.points[0].y
		
		u = (y2*x3-x2*y3)/(y2*x1-x2*y1)
		v = (x3*y1-y3*x1)/(x2*y1-y2*x1)
		
		if boundryIncluded:
			return v >= 0 and u >= 0 and u+v <= 1
		else:
			return v > 0 and u > 0 and u+v < 1

class Quadrangle:
	
	def __init__(self, point1, point2, point3, point4):
		if Line(point1,point2) == Line(point2,point3) or Line(point1,point2) == Line(point2,point4) or \
		   Line(point1,point3) == Line(point3,point4) or Line(point2,point3) == Line(point3,point4):
			self.points = None
			print('---ERROR: TRY TO BUILD A QUADRANGLE WITH SOME POINTS AT THE SAME LINE---')
		self.points = [point1, point2, point3, point4]
	
	@classmethod
	def from_array(cls, points):
		return cls(points[0],points[1],points[2],points[3])
		
	def __str__(self):
		result = '{'
		for p in self.points:
			result += p.__str__() + ', '
		
		return result + '}'
	
	def hasPointInside(self, thePoint, boundryIncluded):
		tri1 = Triangle.from_array(self.points[:-1])
		tri2 = Triangle(self.points[2],self.points[3],self.points[0])
		result = thePoint.isInside(tri1,boundryIncluded) or thePoint.isInside(tri2,boundryIncluded)
		if result == True:
			return True
		elif not boundryIncluded:
			line1 = Line.from_points(self.points[0],self.points[2])
			line2 = Line.from_points(self.points[0],thePoint)
			if line1 == line2:
				return True
		return False
	
	def draw(self):
		turtle.tracer(False)
		turtle.up()
		turtle.goto(self.points[3].x,self.points[3].y)
		turtle.down()
		for p in self.points:
			turtle.goto(p.x,p.y)
		turtle.tracer(True)
	
# turtle.up()
# turtle.goto(q.points[0].x,q.points[0].y)
# turtle.down()
# turtle.goto(q.points[1].x,q.points[1].y)
# turtle.goto(q.points[2].x,q.points[2].y)
# turtle.goto(q.points[3].x,q.points[3].y)
# turtle.goto(q.points[0].x,q.points[0].y)
# turtle.up()
# turtle.tracer(False)

# for i in range(100):
	# x = random.randint(0,150)
	# y = random.randint(0,150)
	
	# p = point(x,y)
	# print(x,y,end = ' ')
	# if p.isInside(q,True):
		# turtle.goto(x,y)
		# turtle.dot()
		# turtle.update()
		# print('Y')
	# else:
		# print(' ')

points = [Point(61.145,168.5), Point(60.281,237.512), Point(220.936,142.949),
		  Point(190.667,91.63),Point(280,85),         Point(330.957,125.766),
		  Point(472,57),       Point(399,32),         Point(459,33),
		  Point(523,58),       Point(533,3),          Point(594,29)]
areas = [Quadrangle(points[1],points[0],points[3],points[2]),
		 Quadrangle(points[2],points[3],points[4],points[5]),
		 Quadrangle(points[5],points[4],points[7],points[6]),
		 Quadrangle(points[6],points[7],points[8],points[9]),
		 Quadrangle(points[9],points[8],points[10],points[11]),]		 

width = 3.56
length = [3.9986, 2.7, 3.82885, 2.73, 3.8817]

def coor_trans(x, y):
	originalCoor = Point(x,y)
	areaIndex = None
	for i, area in enumerate(areas):
		if originalCoor.isInside(area, boundryIncluded = True):
			areaIndex = i
			break
	
	if type(areaIndex) == type(None):
		return None
	
	theArea = areas[areaIndex]
	point1 = theArea.points[0]
	point2 = theArea.points[1]
	point3 = theArea.points[2]
	point4 = theArea.points[3]
	# Get new X
	endPoint = Line.from_points(point1,point4).intersect(Line.from_points(point2,point3))
	thePoint = Line.from_points(originalCoor,endPoint).intersect(Line.from_points(point1,point2))
	new_x = width * thePoint.distance(point2) / point1.distance(point2)
	# Get new Y
	endPoint = Line.from_points(point1,point2).intersect(Line.from_points(point3,point4))
	thePoint = Line.from_points(originalCoor,endPoint).intersect(Line.from_points(point2,point3))
	y_ = length[areaIndex] * thePoint.distance(point2) / point3.distance(point2)
	new_y = y_ + sum(length[:areaIndex])
	
	return (new_x,new_y)
	
def outputJson(jsonPath):
	f = open(jsonPath,'r')
	dicts = json.load(f)
	f.close()
	
	# Set up progress bar
	print('Processing JSON Now')
	total = len(dicts)
	bar = progressbar.ProgressBar(max_value=total).start()
	
	outputDicts = []
	count = 0
	for dict in dicts:
		newCoor = coor_trans(dict['x'],dict['y'])
		if type(newCoor) == type(None):
			continue
		
		dict['x'] = newCoor[0]
		dict['y'] = newCoor[1]
		
		outputDicts.append(dict)
		count += 1
		if count <= total:
			bar.update(count)
	
	bar.finish()
	f = open(os.path.splitext(jsonPath)[0]+'_trans.json','w')
	json.dump(outputDicts,f)
	f.close()
	
if __name__ == '__main__':	
	outputJson('//home//ssongad//Video//20190724_20190724090949_20190724204645_091102//20190724_20190724090949_20190724204645_091102.json')
	
	
	
	
	
	
	