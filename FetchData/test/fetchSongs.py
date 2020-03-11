import urllib.request
import urllib.parse
import re
import os
from html.parser import HTMLParser
import html
import string
import json
import shutil

def fetch_html(url, params = None):
    header = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:70.0) Gecko/20100101 Firefox/70.0'
    }
    request = urllib.request.Request(url, headers=header)
    try:
        reponse = urllib.request.urlopen(request)
        reponse = reponse.read()
        return reponse
    except BaseException as e:
        return None

def process_html(response, output_file_path):
    lines = response.decode('utf-8').split('\n')
    with open(output_file_path, 'w') as output_file:
        for line in lines:
            result = re.search(r'href=\"(https://www.allmusic.com/mood/[^\"]+)\">(.+)</a>', line)
            if result:
                output_file.write(result[1] +',' + result[2] + '\n')

def get_moods_from_file(mood_file_path):
    lists = []
    with open(mood_file_path, 'r') as input_file:
        for line in input_file:
            result = line.split(',')
            if result:
                lists.append([result[0], result[1].strip()])
    return lists

def get_all_musics(lists, output_file_path):
    print('\n----now begin to fetch music information from allmusic----')
    with open(output_file_path, 'w') as output_file:
        output_file.write('mood,link,name\n')
        for [url, mood] in lists:
            actual_url = url + '/songs/mobile'
            html_content = fetch_html(actual_url)
            if html_content is not None:
                lines = html_content.decode('utf-8').split('\n')
                for line in lines:
                    result = re.search(r'href=\"(https://www.allmusic.com/song/[^\"]+)\">(.+)</a>', line)
                    if result:
                        print('+', end='')
                        output_file.write(mood + ',' + result[1] + ',' + result[2] + '\n')
    print('\n----now fetch music information from allmusic over----')

def get_artist_from_href(lyrics_file_path, output_file_path):
    print('\n----now begin to fetch artist information from allmusic----')
    with open(output_file_path, 'w') as output_file:
        with open(lyrics_file_path, 'r') as input_file:
            cnt = 0
            for record in input_file:
                if cnt > 0:
                    tokens = record.split(',')
                    html_content = fetch_html(tokens[1])
                    lines = html_content.decode('utf-8').split('\n')
                    result = re.search(r'<meta itemprop=\"name\" content=\"([^\"]+)\">', lines)
                    if result:
                        items = re.split('-|\|', result[1])
                        output_file.write(items[0] + ',' + items[1] + '\n')
                        print('+', end='')
                else:
                    output_file.write('song_name,artist\n')
                    cnt += 1
    print('\n----now fetch music artist from allmusic over----')

def search_for_lyrics(songs_file_path, output_file_path):
    print('\n----now begin to fetch lyrics links from lyrics----')
    exists = {}

    with open(output_file_path, 'w', encoding='latin-1') as output_file:
        with open(songs_file_path, 'r') as input_file:
            p = HTMLParser()
            cnt = 0
            for record in input_file:
                if cnt > 0:
                    tokens = record.split(',')
                    target_song = p.unescape(tokens[0].strip())
                    target_singer = tokens[1].strip().replace(' ','').lower()
                    if target_song not in exists or target_singer not in exists[target_song]:
                        if target_song not in exists:
                            exists[target_song] = set()
                        exists[target_song].add(target_singer)
                        url = 'https://www.lyrics.com/lyrics/' + urllib.parse.quote(target_song)
                        html_content = fetch_html(url)
                        lines = html_content.decode('latin-1').split('\n')
                        for line in lines:
                            result = re.search(r'<b><a href=\"(/lyric/[^\"]+)\">[^<]+</a></b>', str(line))
                            if result:
                                info = result[1].split('/')
                                cur_song = info[-1].replace('+','').lower()
                                cur_singer = info[-2].replace('+','').lower()
                                if urllib.parse.unquote(cur_song) == target_song.replace(' ','').lower() and cur_singer == target_singer:
                                    output_file.write(target_song + ',' + target_singer + ',' + 'https://www.lyrics.com/' + result[1] + '\n')
                                    print('+', end='')
                                    break

                else:
                    output_file.write('song,singer,link\n')
                    cnt += 1
    print('\n----now fetch lyrics links from lyrics over----')

def get_files_by_songs(links_file_path, output_dir_path):
    os.mkdir(output_dir_path)
    output_dir_path += '/'
    print('\n----now begin to fetch lyrics from lyrics----')
    with open(links_file_path, 'r', encoding='latin-1') as input_file:
        cnt = 0
        p = HTMLParser()
        table = str.maketrans('','',string.punctuation)
        for lines in input_file:
            if cnt > 0:
                items = lines.split(',')
                song_name = items[0]
                singer_name = items[1]
                link = items[2].strip()
                html_content = fetch_html(link)
                lines = html_content.decode('latin-1').split('\n')
                begin = False
                output_file_path = output_dir_path + song_name.translate(table) + '.' + singer_name.translate(table) + '.txt'
                with open(output_file_path, 'w', encoding='utf-8') as output_file:
                    for line in lines:
                        if not begin:
                            result = re.search(r'<pre id=\"lyric-body-text\"', line)
                            if result:
                                begin = True
                        else:
                            result = re.search(r'</pre>', line)
                            if result:
                                break
                            lyrics = re.sub(r'<[^>]+>','', line)
                            output_file.write(lyrics)
                print(cnt, '\tfetch:', song_name)
            cnt += 1
    print('\n----now fetch lyrics from lyrics over----')

def get_songs_dict(lyrics_file_path, songs_file_path):
    dicts = {}
    lyrics_file = open(lyrics_file_path, 'r', encoding='utf-8')
    songs_file = open(songs_file_path, 'r', encoding='utf-8')
    cnt = 0
    table = str.maketrans('','',string.punctuation)
    p = HTMLParser()
    for lyric in lyrics_file:
        line = songs_file.readline()
        song = p.unescape(line)
        if cnt > 0:
            tokens = song.split(',')
            song_name = tokens[0].translate(table).strip()
            mood = lyric.split(',')[0]
            singer_name = tokens[1].translate(table).replace(' ','').lower().strip()
            if song_name not in dicts:
                dicts[song_name] = {}
            if singer_name not in dicts[song_name]:
                dicts[song_name][singer_name] = mood
        else:
            cnt += 1

    return dicts

def get_final_dataset(songs_dict, output_dir_path, final_dir_path):
    os.mkdir(final_dir_path)
    cnt = 0
    for root,dirs,files in os.walk(output_dir_path):
        for file in files:
            file_path = os.path.join(root,file)
            tokens = file.split('.')
            song_name = tokens[0]
            singer_name = tokens[1]
            try:
                mood = songs_dict[song_name][singer_name]
                target_dir = final_dir_path + '/' + mood
                dir_str = '.'
                for dir_part in target_dir.split('/'):
                    dir_str += '/' + dir_part
                    if not os.path.exists(dir_str):
                        os.mkdir(dir_str)
                shutil.copy(file_path, target_dir)
                cnt += 1
                print(cnt)
            except BaseException as e:
                print(e)

def get_word_split(final_dir_path, split_dir_path):
    # os.mkdir(split_dir_path)
    p = HTMLParser()
    for root,dirs,files in os.walk(final_dir_path):
        for file in files:
            file_path = os.path.join(root,file)
            file_dirs = file_path.split('\\')
            file_name = file_dirs.pop()
            file_dirs[0] = split_dir_path
            tmp_dir = '.'
            for dir in file_dirs:
                tmp_dir += '/' + dir
                if not os.path.exists(tmp_dir):
                    os.mkdir(tmp_dir)
            output_file_path = tmp_dir + '/' + file_name
            if not os.path.exists(output_file_path):
                with open(output_file_path, 'w') as output_file:
                    with open(file_path, 'r') as input_file:
                        for line in input_file:
                            url = 'http://corenlp.run/?properties=%7B%22annotators%22%3A%20%22tokenize%2Cssplit%2Clemma%22%2C%20%22date%22%3A%20%222020-03-02T13%3A25%3A32%22%7D&pipelineLanguage=en'
                            html_content = fetch_html(url, urllib.parse.quote(line.strip()))
                            json_content = json.loads(html_content.decode('utf-8'))
                            if len(json_content['sentences']) > 0:
                                for tokens in json_content['sentences'][0]['tokens']:
                                    output_file.write(tokens['lemma'] + ' ')
                        print('finish', file_name)

if __name__ == '__main__':
    mood_file_path = 'mood.csv'
    if not os.path.exists(mood_file_path):
        response = fetch_html('https://www.allmusic.com/moods')
        process_html(response, mood_file_path)
    #lyrics_file_path = 'lyrics.csv'
    #if not os.path.exists(lyrics_file_path):
    #    moods_link_list = get_moods_from_file(mood_file_path)
    #    get_all_musics(moods_link_list, lyrics_file_path)
    #songs_file_path = 'songs.csv'
    #if not os.path.exists(songs_file_path):
    #    get_artist_from_href(lyrics_file_path, songs_file_path)
    #links_file_path = 'links.csv'
    #if not os.path.exists(links_file_path):
    #    search_for_lyrics(songs_file_path, links_file_path)
    #output_dir_path = 'lyrics'
    #if not os.path.exists(output_dir_path):
    #    get_files_by_songs(links_file_path, output_dir_path)
    #final_dir_path = 'moods_lyrics'
    #if not os.path.exists(final_dir_path):
    #    songs_dict = get_songs_dict(lyrics_file_path, songs_file_path)
    #    get_final_dataset(songs_dict, output_dir_path, final_dir_path)
    #split_dir_path = 'split_lyrics'
    #if not os.path.exists(split_dir_path):
    #    get_word_split(final_dir_path, split_dir_path)
    #get_word_split(final_dir_path, split_dir_path)
