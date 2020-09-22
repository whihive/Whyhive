from pathlib import Path
import moviepy.editor as mp
import os
import shutil


def convert_to_mp4_and_add_logo(logo_dir, video_dir):
    def clean_mkdir(path):
        if Path(path).exists():
            shutil.rmtree(path)
        os.makedirs(path)

    out_videos_dir = "converted_videos"
    clean_mkdir(out_videos_dir)        
    
    logo_image = str(os.listdir(logo_dir)[0])
    video_names = os.listdir(video_dir)

    for fn in video_names:
        '''
        try:            
            video = mp.VideoFileClip(video_dir+"/"+ fn)
        except:
            print("Sorry format of file {} is not supported, so the file would be ignored" .format(fn))
            continue
        try:
            logo = (mp.ImageClip(logo_dir+"/"+logo_image)
                    .set_duration(video.duration)
                    .resize(height=40) # if you need to resize...
                    .margin(right=8, top=8, opacity=0.5) # (optional) logo-border padding
                    .set_pos(("right","top")))
        except:
            print("Sorry format of image: {} is not supported" .format(logo_image))
            continue
        '''
        if fn.endswith('.mp4'):
            #final = mp.CompositeVideoClip([video, logo])
            src = video_dir + "/" + fn
            dir = out_videos_dir +"/" + fn
            shutil.copyfile(src,dir)
            #final.write_videofile(out_videos_dir+ "/" +fn)
        '''    
        else:
            try:
                fn_trim = os.path.splitext(fn)[0]
                final = mp.CompositeVideoClip([video, logo])
                final.write_videofile(out_videos_dir+ "/" + fn_trim + ".mp4")
            except:
                print("Sorry format of file {} is not supported!" .format(fn))
                continue
        '''
    return out_videos_dir
