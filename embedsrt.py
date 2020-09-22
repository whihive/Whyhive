import os
import pprint
import subprocess
import sys
import logging
import shutil

# print(subprocess.check_output(['ls']).decode())
# ffmpeg -i infile.mp4 -i infile.srt -c copy -c:s mov_text outfile.mp4
# ffmpeg -i movie.mkv subtitle.srt -map 0 -map 1 -c copy output.mkv
# rootDir = (os.path.dirname(os.path.realpath(__file__)))


def calaulate_paths(rootDir):
    paths = []

    for dirName, subdirList, fileList in os.walk(rootDir):
        logging.info('Found directory: %s' % dirName)

        if len(fileList) == 0:
            continue
        # goes into folder and finds .mp4 and .srt file
        filelst = []
        for fname in fileList:
            filelst.append(fname)

        # places .mp4 and .srt file name into dictionary
        # filedict = {}
        # if len(filelst) == 2:
        #     if ".srt" in filelst[0]:
        #         filedict["srt"] = filelst[0]
        #         filedict["mp4"] = filelst[1]
        #     else:
        #         filedict["srt"] = filelst[1]
        #         filedict["mp4"] = filelst[0]
        for fn in filelst:
            if ".srt" in fn:
                filedict={}
                filedict["srt"] = fn
                filedict["mp4"] = fn[:-4] +".mp4"
                paths.append([filedict, os.path.join(dirName, filedict["mp4"]), os.path.join(dirName, filedict["srt"])])
            # logging.info(filedict)
            # logging.info(dirName)

        # append dictionary to sublist along with path to mp4 and path to srt
        # append sublist to paths
        # paths.append([filedict, os.path.join(dirName, filedict.get("mp4")), os.path.join(dirName, filedict.get("srt")) ])
    return paths


def embed_srt(root_dir):
    # create and config logging object
    logging.basicConfig(level=logging.DEBUG,
                        format=' %(asctime)s - %(levelname)s- %(message)s')

    # when verbosity is DISABLED, run this
    # logging.disable(logging.CRITICAL)

    # creating output folder
    try:
        os.mkdir(os.path.join(root_dir, "output"))
        logging.debug("created 'output' folder")
    except FileExistsError as e:
        logging.debug("'output' folder already exists. deleting folder")
        os.rmdir(os.path.join(root_dir, "output"))
        logging.debug("'output' folder deleted. creating new 'output' folder")
        os.mkdir(os.path.join(root_dir, "output"))
        logging.debug("created 'output' folder")


        pass

    paths = calaulate_paths(root_dir)
    print("hello")
    for i in paths:
        logging.info("starting subtitle encoding of " + str(i[0].get('mp4')))

        # command that will invoke ffmpeg to embert srt as a stream
        #commandtorun = ['ffmpeg', '-i', 'infile', '-i',
        #                'infilesub', '-c', 'copy', '-c:s', 'mov_text', 'outfile']
        commandtorun = ['ffmpeg', '-i', 'infile', '-vf',
                        'subtitles=', 'outfile']
        # infile video
        commandtorun[2] = i[1]

        # infile srt
        commandtorun[4] = 'subtitles='+i[2]
 
        # outfile
        commandtorun[5] = os.path.join(root_dir, "output", i[0].get('mp4')) #changed from 9 to 5
        logging.info("command to run: " + str(commandtorun))

        # # executes command
        commandresult = subprocess.run(commandtorun, stdout=subprocess.PIPE)

        # # ffmpeg output
        logging.info(commandresult.stdout.decode())

        logging.info("completed encoding, starting next")
    
    #The below cell is to ensure that even if the video is without subtiles 
    # the watermarked version of it would still be copied to the output folder
    fn_outputs = os.listdir(os.path.join(root_dir, "output"))
    fn_inputs = []
    for fn in os.listdir(root_dir):
        if fn.endswith(".mp4"):
            fn_inputs.append(fn)
            
    for fn in fn_inputs:
        if fn not in fn_outputs:
            src_dir = os.path.join(root_dir, fn)
            dest_dir = os.path.join(root_dir, "output",fn)
            shutil.copyfile(src_dir, dest_dir
