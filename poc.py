from shutil import rmtree
from pprint import pprint
import sys
import tempfile
import os
import json
import requests
import crx_unpack

class BadExtensionUrl(Exception):
    pass

class GeneralError(Exception):
    pass


# https://chrome.google.com/webstore/detail/<ext_name>/<ext_id>?|/there_could_be_dragons
CHROME_CRX_URL = 'https://clients2.google.com/service/update2/crx?response=redirect&'+ \
                 'prodversion={chrome_version}&acceptformat=crx2&x=id%3D{extension_id}%26uc'

def get_extension(extension_url, chrome_version='72.0.3626.119'):
    ''' extension_url - URL to page in Google Chrome Webstore '''
    # parsing without urlparse
    ext_id = extension_url.split('/')[6]
    ext_id = ext_id.split('?')[0].split('#')[0].split('/')[0]

    req = requests.get(CHROME_CRX_URL.format(chrome_version=chrome_version, extension_id=ext_id))
    if req.status_code == 200:
        tempd = tempfile.mkdtemp()
        tempf = tempfile.mkstemp(dir=tempd, suffix='.crx')
        with open(tempf[1], 'wb') as fh:
            fh.write(req.content)
    elif req.status_code == 404:
        raise BadExtensionUrl
    else:
        raise GeneralError
    return(tempf, tempd)

if __name__ == '__main__':

    if len(sys.argv) == 1:
        with open('input.txt', 'rt') as fh:
            input_data = fh.readlines()
    else:
        input_data = list()
        for x in sys.argv[1:]:
            input_data.append(x)

for url in input_data:
    crx_file, dir_loc = get_extension(url.strip())
    unpacked_dir = os.path.join(dir_loc, 'unpacked')
    crx_unpack.unpack(crx_file[1], ext_dir=unpacked_dir)
    with open(os.path.join(unpacked_dir, 'manifest.json'), 'rt') as f:
        manifest_data = json.load(f)
    # tweek output here
    print(url)
    pprint(manifest_data)
    print('-------------')
    # cleanup
    rmtree(dir_loc)
    
