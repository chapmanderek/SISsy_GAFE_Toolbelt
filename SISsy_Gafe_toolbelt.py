print 'master 0.9'
print 'branch findduplicates v2'

import re
import datetime as dt

#default coloumn locations
google_user_name = 0; google_first_name = 1; google_last_name = 2; google_normalized_name = 7
sis_first_name = 0; sis_last_name = 1; sis_ID = 2; sis_grade = 3; sis_normalized_name = 4
grades = {'08':'17', '07':'18', '06':'19', '8':'17', '7':'18', '6':'19'}

#not need to compare old students
previous_year = 15

#ask for source and destination csv's
ahandle = raw_input('Enter source A file (press enter for google_test_data.csv):')
bhandle = raw_input('Enter source B file (press enter for ic_test_data.csv):')
print '\n'
# open csv files
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
	google_accounts = [each for each in [line.split(',') for line in afile] if len(each) > 3]  #google coloumns are:  email, First Name, Last Name  - 11th coloumn is employee id
	ic_accounts = [each for each in [line.split(',') for line in bfile] if len(each) > 3]  #IC columns:   first name, lastname, ID#, grade -- ammend on a normalized name
except : print 'Loading the CSVs didnt go very well'

#remove header rows
google_accounts.pop(0)
ic_accounts.pop(0)

#remove staff from google to make matching more accurate, only take username as the domain has a digit in it
temp_list = []
for each in google_accounts:
	user_name = each[google_user_name][0:each[google_user_name].find('@')]
	if re.search('[0-9]' , user_name) and not re.search(str(previous_year), user_name): 
		temp_list.append(each)
google_accounts = temp_list

#remove dashes, spaces, and double quotes from list then create a dict with a normalized name with year, basically their username in google
def create_dict_w_normalizedname_sis(l, first_name, last_name):
	temp_dict = dict()
	for each in l:
		normalized_name = each[first_name].translate(None, '- "')[0:1] + each[last_name].translate(None, '- "')	+ grades[each[sis_grade]]
		if normalized_name in temp_dict: 
			normalized_name = each[first_name].translate(None, '- "') + each[last_name].translate(None, '- "')	+ grades[each[sis_grade]]
			print 'SIS Student name already taken. Username set to --> {0}'.format(normalized_name)
		temp_dict[normalized_name] = each
	return temp_dict

def create_dict_with_google_username(l, username):
	temp_dict = dict()
	for each in l:
		dict_key = each[username][0:each[username].find('@')]
		if dict_key in temp_dict : print 'Possible duplicate username in google --> {0}'.format(dict_key)
		temp_dict[dict_key] = each
	return temp_dict

google_accounts = create_dict_with_google_username(google_accounts, google_user_name)
ic_accounts = create_dict_w_normalizedname_sis(ic_accounts[:], sis_first_name, sis_last_name)

print '\nBefore comparison {lista} had {alength} students, {listb} had {blength} students'.format(lista = ahandle[:-4], listb = bhandle[:-4], alength=len(google_accounts), blength =len(ic_accounts))

# check first account against the second for unique accounts using the key which is a normalized name
def find_unique_accounts(base, comparison):
	unique_accounts = dict()
	for each_base in base.keys():
		match = False
		for each_comparison in comparison.keys():
			if each_base == each_comparison:
				match = True
				break
		if match == False : unique_accounts[each_base] = base[each_base]
	return unique_accounts

# check each account for unique files and create new lists
unique_google = find_unique_accounts(google_accounts, ic_accounts)
unique_sis = find_unique_accounts(ic_accounts, google_accounts)

print '{lista} had {alength} unique students, {listb} had {blength} unique students'.format(lista = ahandle[:-4], listb = bhandle[:-4], alength=len(unique_google), blength =len(unique_sis))
print '\n'

# get and format date ready to use for file names
now = dt.datetime.now()
date_mdy = str(now.month) + '-' + str(now.day) + '-' + str(now.year)

#open a new file to write unique accounts on both sides to
file_out_name = 'unique_accounts_{date}.txt'.format(date = date_mdy)
file_out = open(file_out_name, 'w')

file_out.write("-----------------------\nUnique to {0}\n".format(ahandle[:-4]))
file_out.write(str(unique_google))
file_out.write('\n\n')
file_out.write("-----------------------\nUnique to {0}\n".format(bhandle[:-4]))
file_out.write(str(unique_sis))
file_out.write('\n')

file_out.close()

#output unique sis accounts ready to upload into google admin console
gfile_name = 'google_upload_formatted_{date}.csv'.format(date = date_mdy)
gfile_out = open(gfile_name, 'w')

# insert googles header row
blank_google = open("blank_google_upload.csv")
gfile_out.write(blank_google.readline())

#google upload columns -->  First Name,Last Name,Email Address,Password(ID#)
for username in unique_sis:
	line = unique_sis[username][sis_first_name] + ',' + unique_sis[username][sis_last_name] + ',' + username + ',' + unique_sis[username][sis_ID] + '\n'
	gfile_out.write(line)
gfile_out.close()


