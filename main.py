import commands
import requests
import time
import urllib2        #connect to webpage
from bs4 import BeautifulSoup    #class name, python package=bs4

def scan_macids():
    mac_list = []
    for i in range (0, 3):
        scan_cmd_ble = 'sudo timeout -s SIGINT 10s hcitool -i hci0 lescan'
        scan_cmd = 'sudo timeout -s SIGINT 10s hcitool -i hci0 scan'

        #status, ble_out = commands.getstatusoutput(scan_cmd_ble)
        status, out = commands.getstatusoutput(scan_cmd)
        data = out.split('\n')
        count = i+1
        print count, 'scan complete.......'
        #print data
        '''
        data_ble = ble_out.split('\n')
        #print data
        if data_ble:
            for line in data_ble:
                mac = line.split()[0]
                if len(mac) == 17:
                    mac_list.append(mac.lower())
        '''
        if data:
            for line in data:
                if len(line) > 17:
                    mac = line.split()[0]
                    if len(mac) == 17:
                        mac_list.append(mac.lower())

    if mac_list:
        mac_list = list(set(mac_list))
    return mac_list

def data_upload(data):

    for key, value in data.iteritems():
        stu_id, mac_id, status = key, value[0], value[1]
        #print stu_id, mac_id, status


        url = 'https://itublereg.000webhostapp.com/wordpress/student-data/'
        payload = {'stu_id': stu_id, 'mac_id': mac_id, 'status' : status}

        try:
            r = requests.get(url, params=payload)
            print r.status_code
        except:
            print 'Problem uploading data'
def get_stu_mac_ids():
    try :
        web_page = urllib2.urlopen("https://itublereg.000webhostapp.com/wordpress/student-data/").read()  #open and read
        soup = BeautifulSoup(web_page,"html.parser")   #parsing the web page data in html format
        #table = soup.find_all('table')[0]
        #print table
        #print soup
    except urllib2.HTTPError :
        print("HTTPERROR!")
    except urllib2.URLError :
        print("URLERROR!")

    data_found = False
    data_str = ''
    matchObj = soup.findAll("script",type="text/javascript")
    #print matchObj
    for i in range (0, len(matchObj)):
        data = str(matchObj[i])
        #print data
        for line in data.split(';'):
            if 'google.visualization.DataTable()' in line:
                data_found = True
                data_str = data.split(';')
                break

        if data_found:
            break
    return data_str

def format_stu_mac_id(data_str):
    value_array = []
    if data_str:
        for line in data_str:
            if 'addRows' in line:
                value_str = line[line.find("(")+1:line.find(")")]
                values = value_str.split('],\n[')
                #print values, 'values'
                for items in values:
                    j = items.split(',')
                    stu_id, mac_id = j[4].rstrip(), j[5].rstrip(']\n]')[2:-1]
                    value_array.append((int(stu_id), mac_id) )
    #print value_array
    return value_array
def main():
    count = 0
    while(1):
        web_data = get_stu_mac_ids()
        if web_data:
            stu_data = format_stu_mac_id(web_data)

            stu_info = {}
            for item in stu_data:
                stu_info[item[1].lower()] = item[0]

            print 'registered student list'
            print '------------------------'
            print stu_info

            scan_list = scan_macids()
            print 'scan list'
            print '------------------------'
            print scan_list

            attendance = {}

            for mac_id, stu_id in stu_info.iteritems():
                if mac_id in scan_list:
                    attendance[stu_id] = (mac_id, 1)
                else:
                    attendance[stu_id] = (mac_id, 0)


            print 'Attendance Report'
            print '--------------------'
            print attendance

            data_upload(attendance)
            count += 1
            if count == 5:
                break
            time.sleep(30)

#calling main here
main()


