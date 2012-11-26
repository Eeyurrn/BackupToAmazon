import tarfile
import subprocess
import tempfile
import os
#please make sure that S3 module from Amazon was on your sys.path
import boto
from boto.s3.connection import S3Connection
from boto.s3.key import Key
import mimetypes
import datetime


def upload_db_to_Amazons3():
    
    now = datetime.datetime.now()
    #S3 access key
    AWS_ACCESS_KEY_ID = ''
    #S3 secret access key
    AWS_SECRET_ACCESS_KEY = ''
    #S3 bucket name
    BUCKET_NAME = ''
    FILE_PREFIX = ''
    MAX_BACKUPS= 3
    FILE_DIRECTORY = ''
    
    
    datestring = str(now.day)+str(now.month)+str(now.year)
    
    day = str(now.day)
    month = str(now.month)
    year = str(now.year)
    
    datestring = '{0:0>4}{1:0>2}{2:0>2}'.format(year,month,day)
    #Archive name with out any extension(i.e.):
    #what name do you want for the file which is uploaded to AMazon S3
    #please give the name  without any extension
    #Also note that a copy of this file will be stored in the directory where the script resides
    ARCHIVE_NAME = 'redmine_FileBackup_'+datestring
    
    print "///Preparing "+ARCHIVE_NAME+"_archive.tar.gz from the database dump................///"      
    #create  tar.gz for the above two files
    tar = tarfile.open( (os.path.join(os.curdir, ARCHIVE_NAME+"_archive.tar.gz")), "w|gz")
    print "///Adding Data File///"
    tar.add(FILE_DIRECTORY,ARCHIVE_NAME,recursive=True)
    #delete temp files
    tar.close()
    
    #Establish connection
    conn = S3Connection(AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY)
    #get all buckets from amazon S3
    response = conn.get_all_buckets()
    buckets = response
    #is the bucket which you have specified is already there
    flag = False
    #find the bucket name, if true then it carries on
    for bucket in buckets :
        if bucket.name == BUCKET_NAME :
            flag = True
            break;
    
    #if there is no bucket with that name     
    if flag == False:
       print "There is no bucket with name "+BUCKET_NAME+" in ls~~your Amazon S3 account"
       print "Error : Please enter an appropriate bucket name and re-run the script"
       return
       
    k = Key(bucket)
    print "///Bucket name is "+bucket.name+"///"
    
    
    print"///Archive name is " + ARCHIVE_NAME+"_archive.tar.gz///"
    k.key = ARCHIVE_NAME+"_archive.tar.gz"
    if k.exists():
        print "Key Exists" 
    print "///uploading the "+ARCHIVE_NAME+"_archive.tar.gz  file to Amazon S3...............///"
    #upload file to Amazon S3  
    #Uncomment this line to enable uploading to amazon S3
    keys = bucket.get_all_keys()
    
    print "printing All keys"
    shortlist = []
    #Populate collection with keys
    for key in keys:
        print "\t"+key.name
        if FILE_PREFIX in key.name:
            shortlist.append(key)
            print "-"*60+"\n"+ key.name +" added to shortlist"+"\n"+"-"*60
            
    #Isolate and sort the dates from the key names
    dates=[]
    for key in shortlist:
        dates.append(key.name.split('_')[2])
    
    for date in dates:
        print "\t"+date
    dates.sort()
    #Check if there are more than 3 backups if yes, delete all but the 2 newest ones
    targetkey = 0
    if len(shortlist) < MAX_BACKUPS:
        print "Less than "+str(MAX_BACKUPS)+ " no need to remove old backups"
    else:
        for i in range(0,len(shortlist)-(MAX_BACKUPS-1)):
            for key in keys:
                if dates[0] in key.name:
                    key.delete()
                    dates[1:]
    k.set_contents_from_filename(ARCHIVE_NAME+"_archive.tar.gz")


upload_db_to_Amazons3()

