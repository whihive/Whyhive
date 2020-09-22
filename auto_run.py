import os
from sys import argv
from goog import transcribe_gcs
from assert_format_and_logo import convert_to_mp4_and_add_logo
from embedsrt import calaulate_paths, embed_srt
from clean_bucket import delete_from_gcloud
from pathlib import Path

logo_dir = argv[1]
video_dir = argv[2]

#Runs transcription for each file inside the specified directory
def auto_run(logo_dir, video_dir):
    
    # convert videos to mp4 and add logo
    new_videos_dir = convert_to_mp4_and_add_logo(logo_dir, video_dir)
    
    directory = Path(new_videos_dir)
    files = os.listdir(new_videos_dir)
    for file in files:
        os.rename(os.path.join(new_videos_dir, file), os.path.join(new_videos_dir, file.replace(' ', '_')))#Removes any spaces in the file names

    for file in os.listdir(new_videos_dir):     # Get each .mp4 file in directory and run transcription
        if file.endswith(".mp4"):
            file_path = os.path.join(new_videos_dir, file)
            transcribe_gcs(file_path)
            print(file_path)
        else:
            continue
    
    # embed srt
    embed_srt(new_videos_dir)

    #delete bucket contents to avoid costs
    delete_from_gcloud("video-srt")

auto_run(logo_dir, video_dir)
