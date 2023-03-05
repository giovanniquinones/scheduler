# Scheduler 

This script assigns appointment slots for interviews. 

For every interviewee (S), an appointment time slot is assigned with their interviewer of choice (P) while avoiding schedule conflicts for both parties. 

**Usage example:** 

`
python slot_assignment.py S_P.file.txt P.schedule.file.txt Output.assignments.csv see n_interviews 
`

**Test run:**

`
python slot_assignment.py studentInterests.formated.txt 2023.faculty.availability.csv sea.csv 14 4
`
