#!/usr/bin/python
import random
import sys
import numpy as np
from collections import defaultdict



def Read_Students_File(Students_File, Professor_List):
	Prof_Student_Count = defaultdict(set)
	Student_Prof_Count = defaultdict(set)
	Student_Name_id = {}
	i = 0
	with open(Students_File) as S:
		next(S)
		for line in S:
			line = line.strip('"').strip()
			Student_Name =  line.split('\t')[0]
			# Student_Name = '{:03d}'.format(int(Student_Name))
                        
			Professors = line.split('\t')[1]
			Student_Name = Student_Name.strip('"')
			i += 1
			Student_id = str(i)
			Student_Name_id[Student_id] = Student_Name
			for Professor in Professors.split(';'):
				Professor = Professor.strip()
				Prof_Student_Count[Professor].add(Student_id)
				Student_Prof_Count[Student_id].add(Professor)
	
	for p, s_list in list(Prof_Student_Count.items()):
		if p not in Professor_List:
			Prof_Student_Count.pop(p)
			sys.stderr.write(f"Professor {p} does not have availability\n")
			for s in s_list:
				Student_Prof_Count[s].remove(p)

	return Prof_Student_Count, Student_Prof_Count, Student_Name_id



def Read_Professors_File(Professors_File):
	Professors_Slots = defaultdict(list)
	with open(Professors_File) as P:
		title = False
		for line in P:
			if not title:
				Time_Slots = line.strip().split(',')[1:]
				title = True
			else:
				L = line.strip().split(',')
				Yes_indexes = np.where(np.array(L[1:]) == "yes")[0]
				Professor_name = L[0]
				for i in Yes_indexes:
					Professors_Slots[Professor_name].append(Time_Slots[i])
	Professor_names = list(Professors_Slots.keys())
	P = len(Professor_names)
	T = len(Time_Slots)
	mat = np.zeros((P, T)).astype(str)
	for Professor, Times in Professors_Slots.items():
		i = Professor_names.index(Professor)
		for Time in Times:
			j = Time_Slots.index(Time)
			mat[i][j] = "Ava"
	return mat, Professor_names, Time_Slots



def reassignment(Student_Prof_Count, Prof_Student_Count, Mat, P, n_interviews):
	### Balancing number of professors and students
	### Select 3 professors for students that selected more

	reassignment = True

	while reassignment:

		reassignment = False 

		for s, Prof_List in Student_Prof_Count.items():
			if len(Prof_List) > n_interviews:
				reassignment  =  True 

				Prof_List = list(Prof_List)
				prof_weights = []

				# prof with more busy slots have higher weight
				for p in Prof_List:
					prof_avail_n = np.count_nonzero(Mat[P.index(p)] == "Ava")
					w_i = max(len(Prof_Student_Count[p]) - prof_avail_n, 0.1)
					prof_weights.append(float(w_i))
				
				prof_weights = np.array(prof_weights)
				prof_weights = prof_weights/np.sum(prof_weights) 


				p = np.random.choice(Prof_List, p = prof_weights)
				Prof_Student_Count[p].remove(s)
				Student_Prof_Count[s].remove(p)

			elif len(Prof_List) < n_interviews:
				reassignment  =  True 

				other_P = list(set(P) - Prof_List)
				prof_weights = [] 

				for p in other_P:
					prof_avail_n = np.count_nonzero(Mat[P.index(p)] == "Ava")
					w_i = max(prof_avail_n - len(Prof_Student_Count[p]), 0.1)
					prof_weights.append(float(w_i))

				prof_weights = np.array(prof_weights)
				prof_weights = prof_weights/np.sum(prof_weights)

				p = np.random.choice(other_P, p = prof_weights)
				Prof_Student_Count[p].add(s)
				Student_Prof_Count[s].add(p)



if __name__ == "__main__":

	Students_File, Professors_File, output_file, Seed, n_interviews = sys.argv[1:6]

	np.random.seed(int(Seed)) 
	n_interviews = int(n_interviews)

	for _ in range(50):	

		Mat, P, T = Read_Professors_File(Professors_File)
		Prof_Student_Count, Student_Prof_Count, Student_Name_id = Read_Students_File(Students_File, P)

		reassignment(Student_Prof_Count, Prof_Student_Count, Mat, P, n_interviews)

		p_weights = dict((p, len(slist)) for p, slist in Prof_Student_Count.items())

		Solution_Found = True 


		for p in sorted(p_weights, key = p_weights.get, reverse=True):
			i = P.index(p)
			js = np.where(Mat[i] == "Ava")[0]
			student_list = list(Prof_Student_Count[p])
			random.shuffle(student_list)

			students_assigned = set()

			for j in js:	
				for student in student_list:
					if student not in Mat[i,:] and student not in Mat[:,j]:
						Mat[i][j] = student 
						students_assigned.add(student) 
						break

			if len(students_assigned) != len(student_list):
				Solution_Found = False 

			
		if Solution_Found:
			sys.stderr.write("... Writing output File\n")

			outf = open(output_file, 'w')
			outf.write(','.join(['Student'] + [t for t in T]) + '\n')

			for s, c in Student_Prof_Count.items():

				times = ["-"]*len(T)
				Prof_n = 0 
				for (i, j) in zip(*np.where(Mat == s)):
					times[j] = P[i]
					Prof_n += 1 

				outf.write(f'"{Student_Name_id[s]}",' + ','.join(times) + f',{Prof_n}\n')

			outf.write('\n')
			outf.write(','.join(['Faculty'] + [t for t in T]) + '\n')
			
			for i in range(Mat.shape[0]):
				times = [P[i]]
				name_count = 0
				for j in range(Mat.shape[1]):
					if Mat[i][j] in ('0.0', 'Ava'):
						times.append('-')
					else:
						name = Student_Name_id[Mat[i][j]][:20]
						name_count += 1
						times.append(f'"{name}"')
					
				outf.write(','.join(times) + f',{name_count}\n')

			outf.close()

			Prof_Student_Count, original_Student_Prof_Count, Student_Name_id = Read_Students_File(Students_File, P)

			for s, original_prof_list in original_Student_Prof_Count.items():
				prof_list = Student_Prof_Count[s]
				common = original_prof_list & prof_list
				sys.stderr.write(f'student = "{Student_Name_id[s]}" assigned = {len(common)}; not assigned = {len(original_prof_list) - len(common)} {original_prof_list-common}\n')
			break
			
