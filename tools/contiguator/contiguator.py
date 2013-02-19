"""
run_contiguator.py
A wrapper script for Contiguator
Peter Li peter@gigasciencejournal.com
"""

import sys, optparse, os, tempfile, shutil, subprocess, re, fnmatch

def stop_err(msg):
    sys.stderr.write('%s\n' % msg)
    sys.exit()

def cleanup_before_exit(tmp_dir):
    if tmp_dir and os.path.exists(tmp_dir):
        shutil.rmtree(tmp_dir)

def html_report_from_directory(html_out, dir):
    html_out.write('<html>\n<head>\n</head>\n<body>\n<font face="arial">\n<p>Contiguator output</p>\n<p/>\n')
    for dirname, dirnames, filenames in os.walk(dir):
        #Print path to subdir
        for subdirname in dirnames:
            html_out.write('<p>Folder: ' + subdirname + '<p>\n')
            #List subdir files
            files = os.listdir(os.path.join(dirname, subdirname))
            for filename in files:
                html_out.write('\t<li><a href="%s">%s</a></li>\n' % (os.path.join(subdirname, filename), filename))
        #Print log
        for file in filenames:
            if fnmatch.fnmatch(file, '*.log'):
                html_out.write('<p><a href="%s">%s</a></p>\n' % (file, file))

    html_out.write('</font>\n</body>\n</html>\n')

def __main__():
    #Parse command line
    parser = optparse.OptionParser()

    #Input params
    parser.add_option('', '--ref_fasta', dest='ref_fasta')
    parser.add_option('', '--contig_scaff_fasta', dest='contig_scaff_fasta')

    parser.add_option("", "--default_full_settings_type", dest="default_full_settings_type")
    #Custom params
    parser.add_option("", "--log_level", dest="log_level")
    parser.add_option("", "--more_results", dest="more_results")
    parser.add_option("", "--blast_evalue_threshold", dest="blast_evalue_threshold")
    parser.add_option("", "--contig_minimal_length", dest="contig_minimal_length")
    parser.add_option("", "--contig_minimal_coverage", dest="contig_minimal_coverage")
    parser.add_option("", "--minimal_blast_hit_length", dest="minimal_blast_hit_length")
    parser.add_option("", "--minimum_best_replicon_estimation_ratio", dest="minimum_best_replicon_estimation_ratio")

    #Output
    parser.add_option("", "--html_file", dest="html_file")
    parser.add_option("", "--html_file_files_path", dest="html_file_files_path")
    opts, args = parser.parse_args()

    #Create directory to process and store contiguator outputs
    html_file = opts.html_file
    job_work_dir = opts.html_file_files_path
#    if not os.path.exists(job_work_dir):
#        print "HTML directory does not exist"
#        try:
#            print "Creating directory"
#            #This actually creates a dir in:
#            #./galaxy-central/database/files/000/dataset_139_files
#            #./galaxy-central/database/job_working_directory/000/126/dataset_139_files/Map_gi.225631039.ref.NC.012417.1.
#            os.makedirs(job_work_dir)
#        except:
#            pass

    dirpath = tempfile.mkdtemp(prefix='tmp-contiguator-')

    #Run contiguator
    #Need to give the proper place to where Galaxy stored files
    #Not        ./galaxy-central/database/job_working_directory/000/131/dataset_144_files/
    #Instead    ./galaxy-central/database/files/000/dataset_144_files/
    #So need to replace "job_working_directory/000/131" in between database/ and and /dataset_
    #With "files/000"
    rex = re.compile('database/(.*)/dataset_')
    files_dir = rex.sub("database/files/000/dataset_", job_work_dir)
    files_dir = files_dir + "/"
    #print "New html dir: ", files_dir
    #Create directory
    if not os.path.exists(files_dir):
        #print "HTML directory does not exist"
        try:
            os.makedirs(files_dir)
        except:
            pass

    cmd = "python /usr/local/contiguator/current/CONTIGuator.py -r %s -c %s -f %s"% (opts.ref_fasta, opts.contig_scaff_fasta, files_dir)
    if opts.more_results == "yes":
        cmd =  cmd + " -M"
    if opts.log_level == "debug":
        cmd =  cmd + " -G"
    elif opts.log_level == "development":
        cmd =  cmd + " -D"
    elif opts.log_level == "verbose":
        cmd =  cmd + " -V"

    #sys.stdout.write("Command: " + cmd)
    try:
        tmp_out_file = tempfile.NamedTemporaryFile(dir=dirpath).name
        tmp_stdout = open(tmp_out_file, 'wb')
        tmp_err_file = tempfile.NamedTemporaryFile(dir=dirpath).name
        tmp_stderr = open(tmp_err_file, 'wb')

        #Perform system call
        #print "Contiguator current dir: ", files_dir
        proc = subprocess.Popen(args=cmd, shell=True, cwd=files_dir, stdout=tmp_stdout, stderr=tmp_stderr)
        returncode = proc.wait()
        # get stderr, allowing for case where it's very large
        tmp_stderr = open(tmp_err_file, 'rb')
        stderr = ''
        buffsize = 1048576
        try:
            while True:
                stderr += tmp_stderr.read(buffsize)
                if not stderr or len(stderr) % buffsize != 0:
                    break
        except OverflowError:
            pass

        if returncode != 0:
            raise Exception, stderr

        tmp_stdout.close()
        tmp_stderr.close()

    except Exception, e:
        raise Exception, 'Problem executing Contiguator:\n' + str(e)

    #Generate html
    html_report_from_directory(open(html_file, 'wb'),files_dir)

    #Check status
    if os.path.getsize(html_file) > 0:
        sys.stdout.write('Contiguator process complete')
    else:
        stop_err("Output is empty")

    #Clean up temp files
    cleanup_before_exit(dirpath)

if __name__ == "__main__":
    __main__()
