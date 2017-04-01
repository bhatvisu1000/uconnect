import sys, getopt

def main(argv):

   print len(sys.argv)
   for arg in sys.argv:
      print "Argument:", arg
   if len(sys.argv) == 0:
     print 'usage: getSettings.py -g <global_json_file_path>'
     sys.exit(2) 
   #try:
   opts, args = getopt.getopt(argv,":h:g:",["globalFilePath="])
   for opt, arg in opts:
     if opt == '-h' or opt == '':
        print 'usage: getSettings.py -g <global_json_file_path>'
        sys.exit()
     elif opt in ("-g", "--globalFilePath"):
        globalFilePath = arg
     elif opt == '':
        print 'usage: getSettings.py -g <global_json_file_path>'
        sys.exit()
     print 'Global file path is "', globalFilePath

   #except getopt.GetoptError:
    #  print 'usage: getSettings.py -g <global_json_file_path>'
     # sys.exit(2)

if __name__ == "__main__":
   main(sys.argv[1:])