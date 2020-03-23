import urllib.request
import urllib.parse
import re
import os
import csv
import string
import html
import stanfordnlp
import chardet
import math

table = str.maketrans('','',string.punctuation)
options = ['https://genius.com/',
            'http://www.songlyrics.com/',
            'https://www.musixmatch.com/lyrics/',
            'https://www.musixmatch.com/es/letras/',
            'https://www.azlyrics.com/lyrics/',
            'https://www.lyrics.com/',
            'https://www.karaoke-lyrics.net/',
            'https://lyrics.fandom.com/wiki/',
            'https://www.metrolyrics.com/'
            ]

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

def get_mood_file(url, output_file_path):
    response = fetch_html(url)
    lines = response.decode('utf-8').split('\n')
    with open(output_file_path, 'w') as output_file:
        output_file.write('Index,Mood,Url\n')
        cnt = 0
        for line in lines:
            result = re.search(r'href=\"(https://www.allmusic.com/mood/[^\"]+)\">(.+)</a>', line)
            if result:
                cnt += 1
                output_file.write(str(cnt) + ',' + result[2] + ',' + result[1] + '\n')

def get_songs_file(mood_file_path, songs_file_path):
    songs_dict = set()
    with open(mood_file_path, 'r') as input_file:
        cnt = 0
        for line in input_file:
            if cnt > 0:
                record = line.split(',')
                url = record[2].strip() + '/songs/mobile'
                html_content = fetch_html(url)
                if html_content is not None:
                    lines = html_content.decode('utf-8').split('\n')
                    for line in lines:
                        result = re.search(r'href=\"(https://www.allmusic.com/song/[^\"]+)\">(.+)</a>', line)
                        if result:
                            songs_dict.add(result[1])
            else:
                cnt += 1
    with open(songs_file_path, 'w') as output_file:
        spamwriter = csv.writer(output_file, delimiter=',', quotechar='\"', quoting=csv.QUOTE_MINIMAL)
        spamwriter.writerow(['Index', 'Title', 'Artist', 'Mood'])
        cnt = 1
        for url in songs_dict:
            title, artist, mood = get_song_infomation(url)
            if 'Relaxed' in mood:
                spamwriter.writerow([cnt, title, artist, 'Relaxed'])
                cnt += 1
                print(cnt)
            elif 'Angry' in mood:
                spamwriter.writerow([cnt, title, artist, 'Angry'])
                cnt += 1
                print(cnt)
            elif 'Happy' in mood:
                spamwriter.writerow([cnt, title, artist, 'Happy'])
                cnt += 1
                print(cnt)
            elif 'Sad' in mood:
                spamwriter.writerow([cnt, title, artist, 'Sad'])
                cnt += 1
                print(cnt)

def get_song_infomation(url):
    html_content = fetch_html(url)
    lines = html_content.decode('utf-8').split('\n')
    title, artist = None, None
    mood = {}
    isBegin = False
    for line in lines:
        result = re.search(r'<meta name=\"title\" content=\"([^|]+)\|[^|]+\|[^|]+\">', line)
        if result:
            items = re.split(' - ', result[1])
            title, artist = html.unescape(items[0]), html.unescape(items[1])
        if not isBegin:
            result = re.search(r'<div class=\"song_moods\">', line)
            if result:
                isBegin = True
        else:
            result = re.search(r'<a href=\"/mood/[^\"]+\">([^<]+)</a>', line)
            if result:
                link = result[1].split(' ')
                mood[link[0]] = int(link[1].replace(')', '').replace('(', ''))
            result = re.search(r'<div class=\"song_themes\">', line)
            if result:
                isBegin = False
    return title, artist, mood

def get_url_by_option(option, title, artist):
    global table
    url = None
    if option == 'https://genius.com/':
        target_artist = artist.replace('-',' ').replace('&', 'and').translate(table).replace(' ', '-')
        target_title = title.replace('-',' ').replace('&', 'and').translate(table).replace(' ','-')
        url = option + target_artist + '-' + target_title + '-' + 'lyrics'
    elif option == 'https://www.musixmatch.com/lyrics/':
        target_artist = artist.replace('-',' ').replace('&', 'and').translate(table).replace(' ', '-')
        target_title = title.replace('-',' ').translate(table).replace(' ','-')
        url = option + target_artist + '/' + target_title
    elif option == 'https://www.musixmatch.com/es/letras/':
        target_artist = artist.replace('-',' ').replace('&', 'and').translate(table).replace(' ', '-')
        target_title = title.replace('-',' ').translate(table).replace(' ','-')
        url = option + target_artist + '/' + target_title
    elif option == 'https://www.azlyrics.com/lyrics/':
        target_artist = artist.translate(table).replace(' ','').lower()
        target_artist = target_artist.replace('the', '')
        target_title = re.sub(r'\([^\)]+\)','', title)
        target_title = target_title.translate(table).replace(' ','').lower()
        url = option + target_artist + '/' + target_title + '.html'
    elif option == 'https://www.metrolyrics.com/':
        target_artist = artist.translate(table).replace(' ', '-')
        target_title = title.translate(table).replace(' ','-')
        url = option + target_title + '-' + 'lyrics' + '-' + target_artist
    elif option == 'https://www.lyrics.com/':
        target_title = title
        target_artist = artist
        current_url = option + 'lyrics/' + urllib.parse.quote(target_title)
        html_content = fetch_html(current_url)
        lines = None
        try:
            lines = html_content.decode('utf-8').split('\n')
        except BaseException as e:
            lines = html_content.decode('latin-1').split('\n')
        for line in lines:
            result = re.search(r'<b><a href=\"(/lyric/[^\"]+)\">[^<]+</a></b>', line)
            if result:
                info = result[1].split('/')
                current_title = info[-1].replace('+', ' ').lower()
                current_artist = info[-2].replace('+', ' ').lower()
                if (current_artist.find(target_artist.lower()) != -1
                        or target_artist.lower().find(current_artist.lower()) != -1) \
                        and current_title == target_title.lower():
                    url = option + result[1]
                    break
            result = re.search(r'href=[\'\"](?:https://www.lyrics.com)?(/lyric/[^\'\"]+)[\'\"]', line)
            if result:
                info = result[1].split('/')
                current_title = urllib.parse.unquote(info[-1].replace('+', ' ').lower())
                current_artist = urllib.parse.unquote(info[-2].replace('+', ' ').lower())
                if (current_artist.find(target_artist.lower()) != -1
                        or target_artist.find(current_artist.lower()) != -1) \
                        and current_title == target_title.lower():
                    url = option + result[1]
                    break
    elif option == 'https://www.karaoke-lyrics.net/':
        target_artist = artist.replace('&', 'and').translate(table)
        target_title = title.translate(table).replace(' ','+')
        current_url = option + 'search?q=' + target_title
        html_content = fetch_html(current_url)
        if html_content:
            try:
                lines = html_content.decode('utf-8').split('\n')
            except BaseException as e:
                lines = html_content.decode('latin-1').split('\n')
            for line in lines:
                result = re.search(r'<span class=\"searchresrow_songs\"><a href=\"(/lyrics/[^\"]+)\"', line)
                if result:
                    info = result[1].split('/')
                    current_title = info[-1].translate(table).replace(' ', '').lower()
                    current_artist = info[-2].translate(table).replace(' ', '').lower()
                    if (current_artist.find(target_artist.lower()) != -1
                            or target_artist.lower().find(current_artist.lower()) != -1) \
                            and current_title.find(target_title.replace('+','').lower()) != -1:
                        url = option + result[1]
                        break
    elif option == 'https://lyrics.fandom.com/wiki/':
        target_artist = artist.translate(table).replace(' ','_')
        target_artist = target_artist.replace('the', '')
        target_title = title.translate(table).replace(' ','_')
        url = option + target_artist + ':' + target_title
    elif option == 'http://www.songlyrics.com/':
        target_artist = artist.replace('-',' ').translate(table).replace(' ', '-').lower()
        target_title = title.replace('-',' ').translate(table).replace(' ','-')
        url = option + target_artist + '/' + target_title + '-' + 'lyrics'
    if url is not None:
        return url.replace('--', '-')
    else:
        return None

def get_lyrics_links(songs_file_path, lyrics_link_path):
    global options
    isCrashed = False
    total_lines = 0
    with open(songs_file_path, 'r', newline='', encoding='utf-8') as input_file:
        total_lines = len(input_file.readlines()) - 1
    with open(songs_file_path, 'r') as input_file:
        spamreader = csv.reader(input_file, delimiter=',', quotechar='\"')
        cnt = 0
        with open(lyrics_link_path, 'w') as output_file:
            spamwriter = csv.writer(output_file, delimiter=',', quotechar='\"', quoting=csv.QUOTE_MINIMAL)
            for record in spamreader:
                if cnt > 0:
                    title = record[1].strip()
                    artist = record[2].strip()
                    mood = record[3].strip()
                    html_content = None
                    for option in options:
                        url = get_url_by_option(option, title, artist)
                        if url is not None:
                            html_content = fetch_html(url)
                            if html_content is not None:
                                spamwriter.writerow([str(cnt), title, artist, mood, url])
                                break
                    if html_content is None:
                        spamwriter.writerow([str(cnt), title, artist, mood])
                        print(cnt, artist, title, end='\n')
                        # isCrashed = True
                        # break
                    else:
                        print(cnt, '/', total_lines, end='\n')
                else:
                    spamwriter.writerow(['Index', 'Title', 'Artist', 'Mood', 'Link'])
                cnt += 1
    if isCrashed:
        os.remove(lyrics_link_path)

def get_lyrics_without_encoding(output_file, link, html_content):
    line_cnt = 0
    if link.find('https://genius.com/') != -1:
        lines = html_content.decode('utf-8').split('\n')
        isBegin = False
        current_str = ''
        for line in lines:
            if not isBegin:
                if line.strip() == '<div class=\"lyrics\">':
                    isBegin = True
            else:
                if line.strip() == '</div>':
                    isBegin = False
                    result = re.sub(r'<[^<>]+>', '\n', current_str)
                    for segment in result.split('\n'):
                        if len(segment) > 0:
                            output_file.write(segment + '\n')
                            line_cnt += 1
                else:
                    current_str += line.strip()
    elif link.find('https://www.azlyrics.com/lyrics/') != -1:
        lines = html_content.decode('utf-8').split('\n')
        for line in lines:
            result = re.match(r'([^<]+)<br>', line)
            if result:
                output_file.write(result[1] + '\n')
                line_cnt += 1
    elif link.find('https://www.metrolyrics.com/') != -1:
        lines = html_content.decode('utf-8').split('\n')
        isBegin = False
        current_str = ''
        for line in lines:
            if not isBegin:
                if line.strip() == '<div class=\"lyrics-body\">':
                    isBegin = True
            else:
                if line.find('</div>') != -1:
                    isBegin = False
                    result = re.sub(r'<[^<>]+>', '\n', current_str)
                    for segment in result.split('\n'):
                        if len(segment) > 0:
                            output_file.write(segment + '\n')
                            line_cnt += 1
                else:
                    current_str += line.strip()
    elif link.find('https://www.lyrics.com/') != -1:
        lines = html_content.decode('utf-8').split('\n')
        begin = False
        for line in lines:
            if not begin:
                result = re.search(r'<pre id=\"lyric-body-text\"', line)
                if result:
                    begin = True
            else:
                result = re.search(r'</pre>', line)
                if result:
                    break
                lyrics = re.sub(r'<[^>]+>', '', line)
                output_file.write(lyrics)
                line_cnt += 1
    elif link.find('https://www.karaoke-lyrics.net/') != -1:
        lines = html_content.decode('utf-8').split('\n')
        for line in lines:
            result = re.match(r'([^<]+)<br\s?/?>', line)
            if result:
                output_file.write(result[1] + '\n')
                line_cnt += 1
    elif link.find('https://lyrics.fandom.com/wiki/') != -1:
        lines = html_content.decode('utf-8').split('\n')
        res = None
        for line in lines[919:]:
            result = re.match(r'<div class=\'lyricbox\'>', line)
            if result:
                res = line
                break
        if res is not None:
            res = re.sub('<div class=\'lyricbox\'>', '', html.unescape(res))
            res = res.split('<br />')
            output_file.write('\n'.join(res))
            line_cnt += len(res)
    elif link.find('http://www.songlyrics.com/') != -1:
        lines = html_content.decode('utf-8').split('\n')
        for line in lines:
            result = re.match(r'([^<]+)<br />', line)
            if result:
                output_file.write(result[1] + '\n')
                line_cnt += 1
    elif link.find('https://www.musixmatch.com/') != -1:
        lines = html_content.decode('utf-8').split('\n')
        isBegin = False
        for line in lines:
            if not isBegin:
                result = re.search(r'<span class=\"lyrics__content__[^\"]*\">(.+)', line)
                if result:
                    output_file.write(result[1] + '\n')
                    isBegin = True
                    line_cnt += 1
            else:
                result = re.search(r'([^<]+)</span>', line)
                if result:
                    output_file.write(result[1] + '\n')
                    isBegin = False
                else:
                    output_file.write(line + '\n')
                line_cnt += 1
    return line_cnt

def get_lyrics(lyrics_link_path, lyrics_dir_path, debug_mode = 0):
    os.mkdir(lyrics_dir_path)
    lyrics_dir_path += '/'
    total_lines = 0
    with open(lyrics_link_path, 'r', newline='', encoding='utf-8') as input_file:
        total_lines = len(input_file.readlines()) - 1
    with open(lyrics_link_path, 'r', encoding='utf-8') as input_file:
        spamreader = csv.reader(input_file, delimiter=',', quotechar='\"')
        cnt = 0
        for record in spamreader:
            if cnt > 0 and len(record) == 4:
                if cnt > debug_mode:
                    file_name = record[0]
                    link = record[3]
                    html_content = fetch_html(link)
                    output_file_path = lyrics_dir_path + file_name + '.txt'
                    if not os.path.exists(output_file_path):
                        line_cnt = 0
                        if line_cnt == 0:
                            try:
                                with open(output_file_path, 'w', encoding='latin-1') as output_file:
                                    line_cnt = get_lyrics_without_encoding(output_file, link, html_content)
                            except BaseException as e:
                                os.remove(output_file_path)
                        if line_cnt == 0:
                            try:
                                with open(output_file_path, 'w', encoding='utf-8') as output_file:
                                    line_cnt = get_lyrics_without_encoding(output_file, link, html_content)
                            except BaseException as e:
                                os.remove(output_file_path)
                        if line_cnt == 0:
                            print(cnt, '/', total_lines, line_cnt, link, end='\n')
                        else:
                            print(cnt, '/', total_lines, line_cnt, end='\r')
                    else:
                        print(cnt, '/', total_lines, '-- existing!', end='\r')
            cnt += 1

def get_words_split_for_one_file(file_path, lyrics_dir_path, words_dir_path, nlp):
    lyrics_dir_path += '/'
    words_dir_path += '/'
    input_file_path = lyrics_dir_path + file_path
    with open(input_file_path, 'rb') as input_file:
        data = input_file.read()
        encoding = chardet.detect(data)
    output_file_path = words_dir_path + file_path
    with open(input_file_path, 'r', encoding=encoding['encoding']) as input_file:
        try:
            with open(output_file_path, 'w', encoding=encoding['encoding']) as output_file:
                for line in input_file:
                    line = re.sub(r'\[[^\]]+\]', '', line)
                    line = re.sub(r'\([^\)]+\)', '', line)
                    line = line.strip()
                    if len(line) > 0:
                        words = nlp(line)
                        for sent in words.sentences:
                            for word in sent.words:
                                output_file.write(word.lemma + ' ')
        except BaseException as e:
            os.remove(output_file_path)

def get_balanced_testset(lyrics_link_path, balanced_file_path):
    labels = None
    lists = []
    mood_dict = {
        'Relaxed': [],
        'Sad': [],
        'Happy': [],
        'Angry': []
    }
    with open(lyrics_link_path, 'r', encoding='utf-8') as lyrics_link:
        cnt = 0
        spamreader = csv.reader(lyrics_link, delimiter=',', quotechar='\"')
        for record in spamreader:
            if cnt > 0:
                if len(record) == 5:
                    mood_dict[record[3]].append(record)
            else:
                labels = record
            cnt += 1
    with open(balanced_file_path, 'w', encoding='utf-8') as balanced_file:
        spamwriter = csv.writer(balanced_file, delimiter=',', quotechar='\"', quoting=csv.QUOTE_MINIMAL)
        spamwriter.writerow(labels)
        min_len = min(len(mood_dict['Relaxed']), len(mood_dict['Sad']), len(mood_dict['Happy']), len(mood_dict['Angry']))
        for i in range(min_len):
            spamwriter.writerow(mood_dict['Relaxed'][i])
            spamwriter.writerow(mood_dict['Sad'][i])
            spamwriter.writerow(mood_dict['Happy'][i])
            spamwriter.writerow(mood_dict['Angry'][i])

if __name__ == '__main__':
    mood_list_file_path = 'mood_list.csv'
    if not os.path.exists(mood_list_file_path):
        get_mood_file('https://www.allmusic.com/moods', mood_list_file_path)
    songs_file_path = 'songs_list.csv'
    if not os.path.exists(songs_file_path):
        get_songs_file(mood_list_file_path, songs_file_path)
    lyrics_link_path = 'lyrics_links.csv'
    if not os.path.exists(lyrics_link_path):
        get_lyrics_links(songs_file_path, lyrics_link_path)
    lyrics_dir_path = 'lyrics'
    if not os.path.exists(lyrics_dir_path):
        get_lyrics(lyrics_link_path, lyrics_dir_path)
    words_dir_path = 'words'
    if not os.path.exists(words_dir_path):
        os.mkdir(words_dir_path)
        nlp = stanfordnlp.Pipeline(processors='tokenize,lemma', models_dir='/Users/hangjiezheng/Desktop/CSCI534/')
        for root, dirs, files in os.walk(lyrics_dir_path):
            for input_file_path in files:
                get_words_split_for_one_file(input_file_path, lyrics_dir_path, words_dir_path, nlp)
    balanced_file_path = 'balanced.csv'
    if not os.path.exists(balanced_file_path):
        get_balanced_testset(lyrics_link_path, balanced_file_path)
