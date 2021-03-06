import urllib.request
import urllib.parse
import re
import os
from html.parser import HTMLParser
import html
import string
import csv
import stanza
import chardet

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
stop_words = {'ourselves', 'hers', 'between', 'yourself', 'but', 'again', 'there', 'about', 'once', 'during', 'out', 'very', 'having', 'with', 'they', 'own', 'an', 'be', 'some', 'for', 'do', 'its', 'yours', 'such', 'into', 'of', 'most', 'itself', 'other', 'off', 'is', 's', 'am', 'or', 'who', 'as', 'from', 'him', 'each', 'the', 'themselves', 'until', 'below', 'are', 'we', 'these', 'your', 'his', 'through', 'don', 'nor', 'me', 'were', 'her', 'more', 'himself', 'this', 'down', 'should', 'our', 'their', 'while', 'above', 'both', 'up', 'to', 'ours', 'had', 'she', 'all', 'no', 'when', 'at', 'any', 'before', 'them', 'same', 'and', 'been', 'have', 'in', 'will', 'on', 'does', 'yourselves', 'then', 'that', 'because', 'what', 'over', 'why', 'so', 'can', 'did', 'not', 'now', 'under', 'he', 'you', 'herself', 'has', 'just', 'where', 'too', 'only', 'myself', 'which', 'those', 'i', 'after', 'few', 'whom', 't', 'being', 'if', 'theirs', 'my', 'against', 'a', 'by', 'doing', 'it', 'how', 'further', 'was', 'here', 'than'}

def fetch_html(url):
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
        target_artist = artist.translate(table).replace(' ', '-').replace('--','-')
        target_title = title.translate(table).replace(' ','-')
        url = option + target_title + '-' + 'lyrics' + '-' + target_artist
    elif option == 'https://www.lyrics.com/':
        target_title = title
        target_artist = artist
        current_url = option + 'lyrics/' + urllib.parse.quote(target_title)
        html_content = fetch_html(current_url)
        lines = html_content.decode('utf-8').split('\n')
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
        lines = html_content.decode('utf-8').split('\n')
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
    return url

def search_for_songs(songs_file_path, output_file_path, debug_mode = 0):
    global options
    print('\n----now begin to fetch lyrics links from lyrics----')
    isCrashed = False
    total_lines = 0
    with open(songs_file_path, 'r', newline='', encoding='utf-8') as input_file:
        total_lines = len(input_file.readlines()) - 1
    with open(output_file_path, 'w', newline='', encoding='utf-8') as output_file:
        with open(songs_file_path, 'r', newline='', encoding='utf-8') as input_file:
            p = HTMLParser()
            cnt = 0
            spamreader = csv.reader(input_file, delimiter=',', quotechar='\"')
            spamwriter = csv.writer(output_file, delimiter=',', quotechar='\"', quoting=csv.QUOTE_MINIMAL)
            for record in spamreader:
                if cnt > 0:
                    if cnt > debug_mode:
                        artist = record[1].strip()
                        title = record[2].strip()
                        html_content = None
                        for option in options:
                            url = get_url_by_option(option, title, artist)
                            if url is not None:
                                html_content = fetch_html(url)
                                if html_content is not None:
                                    if url.find('https://genius.com/') == -1:
                                        print(cnt, artist, ',', title)
                                    spamwriter.writerow(record + [url])
                                    break
                        if html_content is None:
                            spamwriter.writerow(record)
                            print(cnt, artist, ',', title, end='\r')
                            isCrashed = True
                            break
                        else:
                            print(cnt, '/', total_lines, end='\r')
                    else:
                        print(cnt, '/', total_lines, end='\r')
                    cnt += 1
                else:
                    spamwriter.writerow(record + ['Link'])
                    cnt += 1
    if isCrashed:
        os.remove(output_file_path)
    print('\n----now fetch lyrics links from lyrics over----')

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

def test_extra_link(output_file_path, title, artist):
    global options
    line_cnt = 0
    for option in options:
        link = get_url_by_option(option, title, artist)
        if link is not None:
            html_content = fetch_html(link)
            if html_content is not None:
                if line_cnt == 0:
                    try:
                        with open(output_file_path, 'w', encoding='latin-1') as output_file:
                            line_cnt = get_lyrics_without_encoding(output_file, link, html_content)
                    finally:
                        if line_cnt == 0:
                            os.remove(output_file_path)
                        else:
                            break;
                if line_cnt == 0:
                    try:
                        with open(output_file_path, 'w', encoding='utf-8') as output_file:
                            line_cnt = get_lyrics_without_encoding(output_file, link, html_content)
                    finally:
                        if line_cnt == 0:
                            os.remove(output_file_path)
                        else:
                            break
    return line_cnt

def get_lyrics(links_file_path, output_dir_path, debug_mode = 0):
    if not os.path.exists(output_dir_path):
        os.mkdir(output_dir_path)
    output_dir_path += '/'
    print('\n----now begin to fetch lyrics from lyrics----')
    total_lines = 0
    with open(links_file_path, 'r', newline='', encoding='utf-8') as input_file:
        total_lines = len(input_file.readlines()) - 1
    with open(links_file_path, 'r', encoding='utf-8') as input_file:
        spamreader = csv.reader(input_file, delimiter=',', quotechar='\"')
        cnt = 0
        for record in spamreader:
            if cnt > 0:
                if cnt > debug_mode:
                    file_name = record[0]
                    link = record[4]
                    html_content = fetch_html(link)
                    output_file_path = output_dir_path + file_name + '.txt'
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
                        if line_cnt == 0 and test_extra_link(output_file_path, record[2], record[1]) == 0:
                            print(cnt, '/', total_lines, line_cnt, link, end='\n')
                        else:
                            print(cnt, '/', total_lines, line_cnt, end='\r')
                    else:
                        print(cnt, '/', total_lines, '-- existing!', end='\r')
            cnt += 1
    print('\n----now fetch lyrics from lyrics over----')

def get_words_split(links_file_path, lyrics_dir_path, words_dir_path, debug_mode_low=0, debug_mode_high=3000):
    if not os.path.exists(words_dir_path):
        os.mkdir(words_dir_path)
    lyrics_dir_path += '/'
    words_dir_path += '/'
    nlp = stanza.Pipeline(processors='tokenize,lemma,pos')
    cnt = 0
    total_lines = 0
    table = str.maketrans('', '', string.punctuation)
    with open(links_file_path, 'r', newline='', encoding='utf-8') as links_file:
        total_lines = len(links_file.readlines()) - 1
    with open(links_file_path, 'r', newline='', encoding='utf-8') as links_file:
        with open(songs_file_path, 'r', newline='', encoding='utf-8') as input_file:
            cnt = 0
            spamreader = csv.reader(input_file, delimiter=',', quotechar='\"')
            for record in spamreader:
                if cnt > debug_mode_low and cnt < debug_mode_high:
                    input_file_path = lyrics_dir_path + record[0] + '.txt'
                    output_file_path = words_dir_path + record[0] + '.txt'
                    encoding = ''
                    with open(input_file_path, 'rb') as input_file:
                        data = input_file.read()
                        encoding = chardet.detect(data)
                    with open(input_file_path, 'r', encoding=encoding['encoding']) as input_file:
                        try:
                            with open(output_file_path, 'w', encoding=encoding['encoding']) as output_file:
                                for line in input_file:
                                    line = re.sub(r'\[[^\]]+\]', '', line)
                                    line = re.sub(r'\([^\)]+\)', '', line)
                                    line = re.sub(r'<[^>]+>', '', line)
                                    line = line.strip()
                                    if len(line) > 0:
                                        words = nlp(line)
                                        for sent in words.sentences:
                                            for word in sent.words:
                                                lemma = word.lemma.translate(table)
                                                if len(lemma) > 0:
                                                    output_file.write(word.lemma + ' ')
                                        output_file.write('\n')
                        except BaseException as e:
                            os.remove(output_file_path)
                            print("remove", record[0])
                    print(cnt, '/', total_lines, end='\n')
                cnt += 1

if __name__ == '__main__':
    songs_file_path = 'MoodyLyrics/ml_raw.csv'
    links_file_path = 'lyrics_links.csv'
    if not os.path.exists(links_file_path):
        search_for_songs(songs_file_path, links_file_path, 0)
    lyrics_dir_path = 'lyrics'
    if not os.path.exists(lyrics_dir_path):
        get_lyrics(links_file_path, lyrics_dir_path, 0)
    words_dir_path = 'words'
    if True or not os.path.exists(words_dir_path):
        get_words_split(links_file_path, lyrics_dir_path, words_dir_path)