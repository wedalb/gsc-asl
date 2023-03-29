import requests
import requests_cache
import csv
import pandas as pd
from moviepy.editor import VideoFileClip
import concurrent.futures

session = requests_cache.CachedSession('uta_asllexicon_cache')

ALL_SPEAKERS = [ 'Lana', 'Dana', 'Liz', 'Tyler', 'Naomi', 'Jaimee' ]
speakers = [ 'Tyler' ]
metadata = {}

def download_file(video_name):
    filename = 'data/' + video_name.replace('/', '_')
    url = 'http://vlm1.uta.edu/~haijing/asl/camera1/' + video_name
    try:
        with open(filename, 'xb') as f:
            r = requests.get(url, stream=True)
            print(filename, 'downloading...')
            for chunk in r.iter_content(chunk_size = 16*1024):
                f.write(chunk)
            print(filename, 'downloaded !')
    except FileExistsError:
        print('File', filename, 'already exists!')
    except Exception as e:
        print(e)

for speaker in speakers:
    url = f'http://vlm1.uta.edu/~athitsos/asl_lexicon/csv/uta_handshapes_{speaker.lower()}.csv'
    response = session.get(url)
    data = csv.reader( response.text.split('\r\n') )
    next(data) # discard 1st line
    columns = next(data)
    data = pd.DataFrame(data=data, columns=columns)
    data = data[data['Gloss start'].notnull() & data['Gloss end'].notnull()]
    data['Gloss start'] = data['Gloss start'].astype(int)
    data['Gloss end'] = data['Gloss end'].astype(int)
    metadata[speaker] = data

for speaker in metadata:
    metadata[speaker] = metadata[speaker].query('`Sign gloss`.str.len() == 1')

for speaker in metadata:
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
        executor.map( download_file, metadata[speaker]['MOV'].unique())
    for line in metadata[speaker].iterrows():
        line = line[1]
        try:
            in_filename = 'data/' + line['MOV'].replace('/', '_')
            cropped_video = VideoFileClip(in_filename).subclip(0.017 * line['Gloss start'], 0.017 * line['Gloss end'])
            out_filename = 'results/' + line['Sign gloss'] + ".mp4"
            cropped_video.write_videofile(out_filename, fps=25)
        except FileExistsError:
            print('Output video', line['Sign gloss'], "already exists")
