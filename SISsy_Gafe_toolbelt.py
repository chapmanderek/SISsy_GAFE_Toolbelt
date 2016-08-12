# create an 'error file', have different sections fail 'gracefully'
# format output file to include the date to make it more obvious, also so it doesnt overwrite previous data
# split up some sections into seperate functions
# new task to find duplicates in a file
# perhaps an 'opening' section or help section
print 'v 0.0.7'

import re
import datetime as dt

#default coloumn locations
google_user_name = 0; google_first_name = 1; google_last_name = 2; google_normalized_name = 7
sis_first_name = 0; sis_last_name = 1; sis_ID = 2; sis_grade = 3; sis_normalized_name = 4

#not need to compare old students
previous_year = 15

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
try:
	google_accounts = [each for each in [line.split(',') for line in afile] if len(each) > 3]  #google coloumns are:  email, First Name, Last Name
	ic_accounts = [each for each in [line.split(',') for line in bfile] if len(each) > 3]  #IC columns:   first name, lastname, ID#, grade -- ammend on a normalized name
except:
	print 'Loading the CSVs didnt go very well'

#remove header rows
google_accounts.pop(0)
ic_accounts.pop(0)

#remove staff from google to make matching more accurate, only take username as the domain has a digit in it
temp_list = []
for each in google_accounts:
	at_pos = each[google_user_name].find('@')
	user_name = each[google_user_name][0:at_pos]
	if re.search('[0-9]' , user_name): 
		if not re.search(str(previous_year), user_name) : temp_list.append(each)
google_accounts = temp_list

#remove dashes and spaces, double quotes from google to normalize data
temp_dict = dict()
for each in google_accounts:
	normalized_name = each[google_first_name].translate(None, '- "') + each[google_last_name].translate(None, '- "')	
	temp_dict[normalized_name] = each
google_accounts = temp_dict

#remove dashes, spaces, and double quotes from SIS to normalize data
temp_dict = dict()
for each in ic_accounts:
	normalized_name = each[sis_first_name].translate(None, '- "') + each[sis_last_name].translate(None, '- "')
	temp_dict[normalized_name] = each
ic_accounts = temp_dict

print 'Before comparison {lista} had {alength} students, {listb} had {blength} students'.format(lista = ahandle[:-4], listb = bhandle[:-4], alength=len(google_accounts), blength =len(ic_accounts))

# check google for unique accounts
unique_google = list()
for each_google in google_accounts.keys():
	match = False
	for each_ic in ic_accounts.keys():
		if each_google == each_ic:
			match = True
			break
	if match == False : unique_google.append(google_accounts[each_google])

# check sis for unique accounts
unique_sis = list()
for each_ic in ic_accounts.keys():
	match = False
	for each_google in google_accounts.keys():
		if each_ic == each_google:
			match = True
			break
	if match == False : unique_sis.append(ic_accounts[each_ic])


print '\n{lista} had {alength} unique students, {listb} had {blength} unique students'.format(lista = ahandle[:-4], listb = bhandle[:-4], alength=len(unique_google), blength =len(unique_sis))
print '\n'

# get and format date ready to use for file names
now = dt.datetime.now()
mdy = str(now.month) + '-' + str(now.month) + '-' + str(now.year)

#open a new file to write unique accounts on both sides to
file_out_name = 'unique_accounts_{date}.txt'.format(date = mdy)
file_out = open(file_out_name, 'w')
line = "-----------------------\nUnique to {0}\n".format(ahandle[:-4])
file_out.write(line)
file_out.write(str(unique_google))
file_out.write('\n\n')
line = "-----------------------\nUnique to {0}\n".format(bhandle[:-4])
file_out.write(line)
file_out.write(str(unique_sis))
file_out.write('\n')
file_out.close()

#output ready to upload into google admin console
gfile_name = 'google_upload_formatted_{date}.csv'.format(date = mdy)
gfile_out = open(gfile_name, 'w')
grades = {'08':'17', '07':'18', '06':'19', '8':'17', '7':'18', '6':'19'}

blank_google = open("blank_google_upload.csv")
line = blank_google.readline()
gfile_out.write(line)

#google upload columns -->  First Name,Last Name,Email Address,Password(ID#)
for each in unique_sis:
	formatted_email_address = each[sis_first_name][0] + each[sis_last_name] + grades[each[sis_grade]]
	line = each[sis_first_name] + ',' + each[sis_last_name] + ',' + formatted_email_address + ',' + each[sis_ID] + '\n'
	gfile_out.write(line)
gfile_out.close()


