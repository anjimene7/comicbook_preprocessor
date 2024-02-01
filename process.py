import os, sys
import glob
from xml.etree import ElementTree as ET	
import shutil

if len(sys.argv) == 3:
    print('3 params specified')
    source_folder = sys.argv[1]
    destination_folder = sys.argv[2]
    move_files = True
else:
    print('Wrong parameters passed : {}'.format(sys.argv[1:]))
    print('Usage {} source_folder[STR] destination_folder[STR] move[BOOL]'.format(sys.argv[0]))
    exit(1)

print('======= Parameters =======')
print('source_folder : {}\ndestination_folder : {}\nmove : {}\n=========================='.format(source_folder, destination_folder, move_files))

ignored = ["curated"]
if not os.path.isdir(destination_folder):
    print('Creating destination folder {}...'.format(destination_folder))
    os.mkdir(destination_folder)

def get_all_comics(source_folder, ignored):
    to_add = []
    authors=[x for x in os.listdir(source_folder) if os.path.isdir(source_folder+'/'+x) and x not in ignored]
    for i in authors:
        comics=[x for x in os.listdir(source_folder+'/'+i)]
        for j in comics:
            files=[x for x in glob.glob(source_folder+'/'+i+'/'+j+'/*.cb*')]
            if len(files)>=1:
                to_add.extend(files)
    return to_add

def get_all_covers(source_folder, ignored):
    to_add = []
    authors=[x for x in os.listdir(source_folder) if os.path.isdir(source_folder+'/'+x) and x not in ignored]
    for i in authors:
        comics=[x for x in os.listdir(source_folder+'/'+i)]
        for j in comics:
            files=[x for x in glob.glob(source_folder+'/'+i+'/'+j+'/cover.jpg*')]
            if len(files)>=1:
                to_add.extend(files)
    return to_add

def remove_empty_folders(source_folder, ignored):
    print('Removing empty folders on {}'.format(source_folder))
    dirs = [x for x in os.listdir(source_folder) if os.path.isdir(source_folder+'/'+x) and x not in ignored]
    for dir in dirs:
        print('Removing metadata.opf')
        os.system('find "{}"/"{}" -type f -name "metadata.opf" -delete'.format(source_folder, dir))
        remove_empty_folders(source_folder+'/'+dir, ignored)
        try:
            os.rmdir(source_folder+'/'+dir)
        except OSError as ex:
            if ex.errno == 39:
                print("directory not empty")


def move_comic(comic, move):
    folder = os.path.dirname(comic)
    try:
        tree = ET.parse(folder+'/'+'metadata.opf')
    except FileNotFoundError:
        print('metadata.opf not found for {}, continuing to next...'.format(comic))
        return()
    body = tree.getroot()
    series=''
    series_index=''
    for i in body[0]:
        if i.tag == '{http://www.idpf.org/2007/opf}meta':
            if i.attrib['name'] == 'calibre:series':
                series=i.attrib['content']
            elif i.attrib['name'] == 'calibre:series_index':
                series_index=i.attrib['content']
    if series and series_index:
        new_folder = os.path.join(destination_folder, series)
        new_filename = os.path.join(new_folder, os.path.basename(comic))
        if not os.path.isdir(new_folder):
            os.mkdir(new_folder)
        print('Moving comic to {}'.format(new_filename))
        _=shutil.move(comic, new_filename)
        if os.path.exists(os.path.join(os.path.dirname(comic),'cover.jpg')):
            _=shutil.move(os.path.join(os.path.dirname(comic),'cover.jpg'), new_filename.replace('.cbz','.jpg'))
        print('Removing folder...')
        shutil.rmtree(os.path.dirname(comic))

def move_cover(comic, move):
    new_filename = os.system('find {} '.format())
    print(new_filename)
    print('Moving cover to {}'.format(new_filename))
    _=shutil.move(os.path.join(os.path.dirname(comic),'cover.jpg'), new_filename.replace('.cbz','.jpg'))

to_add=get_all_comics(source_folder, ignored)
covers_to_add=get_all_covers(source_folder, ignored)
for comic in to_add:
    print('Processing {}'.format(os.path.basename(comic)))
    move_comic(comic, move_files)
    print('---------')

for cover in covers_to_add:
    move_cover(cover, move_files)
    print(cover)

if move_files:
    remove_empty_folders(source_folder, ignored)
print('DONE !')

