import numpy as np

def CreateArrayWithSteps(nodes, steps, round_digit = 12):
	#preprocessing of the nodes text
	#print("The nodes and steps used to create array are", nodes, steps)
	if isinstance(nodes, list):
		if len(nodes) > 1:
			assert (len(nodes) == len(steps) + 1)
			res = []
			for i in range(len(nodes)-1):
				segment = list(np.arange(nodes[i], nodes[i+1], steps[i]))
				#print("Segment will be added:", segment)
				res.extend(segment)
			res.append(nodes[-1])
			print("The final array generated is ", res)
			return [round(i, round_digit) for i in res] #round up/down
		elif len(nodes) == 1:
			print("Only one element given in the nodes. Create a single-element list")
			array = [round(i, round_digit) for i in nodes]
			print("Array generated is", array)
			return array
		else:
			print("Nodes has NO element inside. Generation failed.")
			return False
	#If nodes is not a list, then make a list of single element.
	else: return [nodes]