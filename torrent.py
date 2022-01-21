import sys
import requests
import os
import argparse
import exception

#Global vars
pages = {
    'login' : 'https://ncore.pro/login.php',
    'list'  : 'https://ncore.pro/torrents.php'
}

login_credentials = {
    'username'  :   os.environ.get('NCORE_USER'),
    'pass'      :   os.environ.get('NCORE_PASS')
}

inputs = {
    'login': {
        'set_lang'  : 'hu',
        'submitted' : '1',
        'nev'       : login_credentials['username'],
        'pass'      : login_credentials['pass']
    },

    'list': {
        'miszerint'  :  'seeders',
        'hogyan'     :  'DESC',
        'miben'      :  'name'   
    },

    'details': {
        'action'    :   'details'
    }
}

torrentTypes = {
    "xvid_hun":"Film SD\/HU",
    "xvid":"Film SD/EN",
    "dvd_hun":"Film DVDR\/HU",
    "dvd":"Film DVDR/EN",
    "dvd9_hun":"Film DVD9/HU",
    "dvd9":"Film DVD9/EN",
    "hd_hun":"Film HD/HU",
    "hd":"Film HD/EN",
    "xvidser_hun":"Sorozat SD/HU",
    "xvidser":"Sorozat SD/EN",
    "dvdser_hun":"Sorozat DVDR/HU",
    "dvdser":"Sorozat DVDR/EN",
    "hdser_hun":"Sorozat HD/HU",
    "hdser":"Sorozat HD/EN",
    "mp3_hun":"MP3/HU",
    "mp3":"MP3/EN",
    "lossless_hun":"Lossless/HU",
    "lossless":"Lossless/EN",
    "clip":"Klip",
    "game_iso":"Játék PC/ISO",
    "game_rip":"Játék PC/RIP",
    "console":"Konzol",
    "ebook_hun":"eBook/HU",
    "ebook":"eBook/EN",
    "iso":"APP/ISO",
    "misc":"APP/RIP",
    "mobil":"APP/Mobil",
    "xxx_xvid":"XXX SD",
    "xxx_dvd":"XXX DVDR/DVD9",
    "xxx_imageset":"XXX Imageset",
    "xxx_hd":"XXX HD"
}
		

#Initializing the argument parser
parser = argparse.ArgumentParser()

parser.add_argument('-l', '--LIST',         help = 'Shows the torrent page')
parser.add_argument('-g', '--GETTORRENT',   help = 'Downloads the specific torrent file')
parser.add_argument('-v', '--VALUE',        help = 'Value for the passed argument')

args = parser.parse_args()


#Var check
for item in login_credentials.values():
    if item is None:
        raise exception.LoginCredentialsNotSet


#defs
def listTorrents(session):
    # -v cmd line argument stands for passing torrent's name and type in NAME|TYPE format
    name = args.VALUE.split('|')[0]
    type = args.VALUE.split('|')[1]

    # Add name and type to the input dictionary
    inputs['list']['mire']  = name
    inputs['list']['tipus'] = type

    # Send a GET request to nCore -> Torrent page
    res = session.get(pages['list'], params = inputs['list'])

    # List of available torrents as string
    response_text = res.text
    
    # Start position of torrent list container HTML
    first_pos = response_text.find('box_torrent_all') - 12

    # End position of torrent list container HTML 
    last_pos  = response_text.find('<div class="lista_lab">')
    
    # Replace official links with madranszkiSeeds links 
    response_text = response_text.replace('<a href="torrents.php?action=details&', '<a href="DOWNLOAD_LINK?')
    
    with open('result.html', 'w') as f:
        # Import the official nCore css file
        f.writelines('<link rel="stylesheet" href="ncore.css">')

        # Write the html code to the destination file
        f.writelines(response_text[first_pos:last_pos:])

def downloadTorrent(session):
    # -v cmd line argument stands for passing torrent ID
    torrent_id = args.VALUE

    # Add torrent ID to the input dictionary
    inputs['details']['id'] = torrent_id

    # Send a GET request to nCore -> Torrent details
    res = session.get(pages['list'], params = inputs['details'])

    # Response text which contains the torrent download link
    details_text = res.text

    # Start position of torrent link tag
    first_pos = details_text.find('text-transform:uppercase') + 33

    # End position of torrent link tag
    last_pos = details_text.find('">Torrent letöltése')

    # Full download link
    download_link = 'https://ncore.pro/' + details_text[first_pos:last_pos:]

    # Send a GET request to nCore -> Torrent download
    get_torrent = session.get(download_link, allow_redirects = True)

    # Write .torrent content to a new file
    with open(torrent_id + '.torrent', 'wb') as torrent_file:
        torrent_file.write(get_torrent.content)

#main
with requests.Session() as session:
    print('> Attempting to login to ncore.pro with credentials:', login_credentials)

    res = session.post(pages['login'], data = inputs['login'])

    needle = 'Hibás felhasználónév' # This string is in response text if credentials are incorrect

    if needle in res.text:
        raise exception.InvalidUserOrPass
    else:
        print('> Login successfull')

    if args.LIST:
        print('> Got argument LIST : Listing torrents...')

        listTorrents(session)

        print('Task done.')
    elif args.GETTORRENT:
        print('> Got argument GETTORRENT : Downloading torrent...')

        downloadTorrent(session)

        print('Task done.')