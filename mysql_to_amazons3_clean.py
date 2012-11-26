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
    """ function which uploadd mysql database to amazon s3"""
    
    #If you are using this script without django then please 
    #fill the below five variables manually
    now = datetime.datetime.now()
    #S3 access key
    AWS_ACCESS_KEY_ID = ''
    #S3 secret access key
    AWS_SECRET_ACCESS_KEY = ''
    #S3 bucket name
    BUCKET_NAME = ''
    #MYSQL_DUMP_PATH should be the path to the mysqldump executable file
    #To know where  mysqldump executable is present in your local system
    #use the command "which mysqldump".
    MYSQL_DUMP_PATH = 'mysqldump'
    
    datestring = str(now.day)+str(now.month)+str(now.year)
    
    day = str(now.day)
    month = str(now.month)
    year = str(now.year)
    
    datestring = '{0:0>4}{1:0>2}{2:0>2}'.format(year,month,day)
    #Archive name with out any extension(i.e.):
    #what name do you want for the file which is uploaded to AMazon S3
    #please give the name  without any extension
    #Also note that a copy of this file will be stored in the directory where the script resides
    ARCHIVE_NAME = 'redmine_MySQLBackup_'+datestring
    print "///Creating Temporary Files...///"
    t1 = tempfile.NamedTemporaryFile()
    print "Tempfile1 Name: "+t1.name
    t2 = tempfile.NamedTemporaryFile()
    print "Tempfile2 Name: "+t2.name
    
    
    #create structure file    
    proc1 = subprocess.Popen(MYSQL_DUMP_PATH+" -u root -PASSWORD --no-create-info -x -v --all-databases > "+t1.name,shell=True)
    #create data file
    proc3 = subprocess.Popen(MYSQL_DUMP_PATH+" -u root -PASSWORD --no-data -x -v --all-databases > "+t2.name,shell=True)
    
    #create temp files
    proc1.communicate()[0]
    #t1.write()
    proc3.communicate()[0]
    print "///Preparing "+ARCHIVE_NAME+"_archive.tar.gz from the database dump................///"      
    #create  tar.gz for the above two files
    tar = tarfile.open( (os.path.join(os.curdir, ARCHIVE_NAME+"_archive.tar.gz")), "w|gz")
    print "///Adding Data File///"
    tar.add(t1.name,ARCHIVE_NAME+"_data.sql",recursive=True)
    print "///Adding Structure File///"
    tar.add(t2.name,ARCHIVE_NAME+"_struct.sql",recursive=True)    
    #delete temp files
    tar.close()
    t1.close()
    t2.close()
    
    
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
    
    #tardata = open(os.path.join(os.curdir, ARCHIVE_NAME+"_archive.tar.gz") , "rb").read()
    print"///Archive name is " + ARCHIVE_NAME+"_archive.tar.gz///"
    k.key = ARCHIVE_NAME+"_archive.tar.gz"
    if k.exists():
        print "Key Exists" 
    print "///uploading the "+ARCHIVE_NAME+"_archive.tar.gz  file to Amazon S3...............///"
    #upload file to Amazon S3  
    #Uncomment this line to enable uploading to amazon S3
    k.set_contents_from_filename(ARCHIVE_NAME+"_archive.tar.gz")




upload_db_to_Amazons3()

