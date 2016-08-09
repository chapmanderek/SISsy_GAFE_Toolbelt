# have it add to a second list instead of making a duplicate of the first list (possibly faster)
# have it skip over staff
# fix for loop in the removing dashes and spaces
# have it add to a second file instead of making a duplicate of the first
# create default settings for the data file columns instead of using numbers
# create an 'error file', have different sections fail 'gracefully'
# format output file to include the date to make it more obvious, also so it doesnt overwrite previous data
# split up some sections into seperate functions
# new task to find duplicates in a file
# perhaps an 'opening' section or help section

import re

#default coloumn locations
google_user_name = 0; google_first_name = 1; google_last_name = 2
sis_first_name = 0; sis_last_name = 1; sis_ID = 2; sis_grade = 3


#ask for source and destination csv's
ahandle = raw_input('Enter source A file (press enter for google_test_data.csv):')
bhandle = raw_input('Enter source B file (press enter for ic_test_data.csv):')

try:
	if len(ahandle) < 1 : ahandle = 'google_test_data.csv'
	afile = open(ahandle).read().split('\n')
	if len(bhandle) < 1 : bhandle = 'ic_test_data.csv'
	bfile = open(bhandle).read().split('\n')
except:
	print 'one of those files was no good'
	exit()

#load both csv's into lists
google_accounts = [each for each in [line.split(',') for line in afile] if len(each) > 3]  #google coloumns are:  email, First Name, Last Name
ic_accounts = [each for each in [line.split(',') for line in bfile] if len(each) > 3]  #IC columns:   first name, lastname, ID#, grade

print 'sis accounts'
print ic_accounts
#remove header rows
google_accounts.pop(0)
ic_accounts.pop(0)

#to make the matching possibly quicker
google_accounts.sort()  
ic_accounts.sort()

#remove staff to make matching more accurate
temp_list = []
for each in google_accounts:
	at_pos = each[google_user_name].find('@')
	user_name = each[google_user_name][0:at_pos]
	if re.search('[0-9]' , user_name) : temp_list.append(each)
google_accounts = temp_list

#remove dashes from both lists since IC doesnt include them consistently
temp_list = list()
for line in google_accounts:
	l = [each.replace('-', '') for each in line ]
	temp_list.append(l)
	# line[2] = line[2].replace('-', '')
	# line[2] = line[2].replace(' ', '')
google_accounts = temp_list
for each in ic_accounts:
	each[sis_last_name] = each[sis_last_name].replace('-', '')
	each[sis_last_name] = each[sis_last_name].replace(' ', '')

#remove double quotes from google
for line in google_accounts:
	line[google_user_name] = line[google_user_name].replace('"', '')
	line[google_first_name] = line[google_first_name].replace('"', '')
	line[google_last_name] = line[google_last_name].replace('"', '')

#to prevent the for loop getting screwy when removing items
final_google = google_accounts[:]
final_ic = ic_accounts[:]

print 'Before comparison {lista} had {alength} students, {listb} had {blength} students'.format(lista = ahandle[:-4], listb = bhandle[:-4], alength=len(google_accounts), blength =len(ic_accounts))

for each_google in google_accounts:
	for each_ic in ic_accounts:
		# if count < 10 : print each_google[1], each_ic[0], each_google[2], each_ic[1]; count += 1
		if each_google[google_first_name] == each_ic[sis_first_name] and each_google[google_last_name] == each_ic[sis_last_name]:
			try:
				final_ic.remove(each_ic)
				final_google.remove(each_google)
			except:
				print "Found another matcher but removing it didnt go well {0}{2} = {1}{3}".format(each_google[1], each_ic[0], each_google[2], each_ic[1])
			break

print '\n{lista} had {alength} unique students, {listb} had {blength} unique students'.format(lista = ahandle[:-4], listb = bhandle[:-4], alength=len(final_google), blength =len(final_ic))
print '\n'

#open a new file to write unique accounts on both sides to
file_out = open('unique_accounts.txt', 'w')
line = "-----------------------\nUnique to {0}\n".format(ahandle[:-4])
file_out.write(line)
file_out.write(str(final_google))
file_out.write('\n\n')
line = "-----------------------\nUnique to {0}\n".format(bhandle[:-4])
file_out.write(line)
file_out.write(str(final_ic))
file_out.write('\n')
file_out.close()

#output ready for google

gfile_out = open('google_upload_formatted.csv', 'w')  
grades = {'08':'17', '07':'18', '06':'19'}

blank_google = open("blank_google_upload.csv")
line = blank_google.readline()
gfile_out.write(line)

#google upload columns -->  First Name,Last Name,Email Address,Password(ID#)
for each in final_ic:
	formatted_email_address = each[sis_first_name][0] + each[sis_last_name] + grades[each[sis_grade]]

	line = each[sis_first_name] + ',' + each[sis_last_name] + ',' + formatted_email_address + ',' + each[sis_ID] + '\n'
	gfile_out.write(line)
gfile_out.close()


