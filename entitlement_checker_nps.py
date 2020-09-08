#!/usr/bin/env python3

import csv
import json
import sys
import os
import urllib.request
import argparse 

parser = argparse.ArgumentParser(description='PSN Entitlement Checker for NPS')
parser.add_argument('input_file', help='input path of your internal_entitlements.json')
parser.add_argument('--csv', action='store_true', help='output results as csv format(default=tsv format)')
parser.add_argument('--debug', action='store_true', help='extract all items with extra info')
args = parser.parse_args()

psv = 'psv'
ps3 = 'ps3'
psp = 'psp'

type_game = 'GAME'
type_dlc = 'DLC'
type_theme = 'THEME'
type_avatar = 'AVATAR'
type_game_dlc = 'GAME/DLC'

DB_DIR = './db_files/'

def download_db():
    base_url = 'https://raw.githubusercontent.com/1jtp8sobiu/entitlement_checker_nps/master/db_files/'
    dist_dir = DB_DIR
    os.makedirs(dist_dir, exist_ok=True)
    
    files = ['pkg.tsv', 'pkg_exception.tsv', 'zrif.tsv', 'rap.tsv', 'last_updated.txt']
    for file in files:
        urllib.request.urlretrieve(base_url+file, dist_dir+file)


def load_db():
    with open(DB_DIR+'pkg.tsv', newline='') as f:
        pkg_db = f.read()
    with open(DB_DIR+'pkg_exception.tsv', newline='') as f:
        pkg_db += f.read()
    with open(DB_DIR+'zrif.tsv', newline='') as f:
        license_db = f.read()
    with open(DB_DIR+'rap.tsv', newline='') as f:
        license_db += f.read()
        
    return pkg_db, license_db


def get_params(entitlement):
    try:
        pkg = entitlement['drm_def']['drmContents'][0]['contentUrl']
        pkg_domain = pkg.split('/')[2]
        pkg_filename = pkg.split('/')[-1]
    except:
        return None

    if pkg_domain.split('.')[0] not in ['ares', 'zeus', 'hfs']:
        return None

    active_date = entitlement['active_date']
    cid = entitlement['drm_def']['drmContents'][0]['contentId']
    name = entitlement['drm_def']['drmContents'][0]['contentName']
    size = entitlement['drm_def']['drmContents'][0]['contentSize']
    drm_type = entitlement['drm_def']['drmContents'][0]['drmType']
    platform_id = entitlement['drm_def']['drmContents'][0]['platformIds']
    base_game = entitlement['drm_def']['drmContents'][0]['titleName']
    product_id = entitlement['drm_def']['productId']

    if cid == 'EP0001-NPEB01982_00-FC4GAMEPS3000001':
        drm_type = 3

    try:
        package_sub_type = entitlement['game_meta']['package_sub_type']
    except:
        package_sub_type = ''

    try:
        psplus = entitlement['drm_def']['expiration']
        psplus = 'Yes'
    except:
        psplus = ''

    params = {'pkg': pkg,
              'pkg_domain': pkg_domain,
              'pkg_filename': pkg_filename,
              'active_date': active_date,
              'cid': cid,
              'name': name,
              'size': size,
              'drm_type': drm_type,
              'platform_id': platform_id,
              'base_game': base_game,
              'product_id': product_id,
              'package_sub_type': package_sub_type,
              'psplus': psplus}

    return params


def get_platform(platform_id, cid, package_sub_type):
    if platform_id == 2281701376: # (or platform_id == 4293918720 ?)
        platform = psv
        pkg_type = type_game_dlc
        if not cid[7:10] == 'PCS':
            platform = ps3
    elif platform_id == 134217728:
        platform = psv
        pkg_type = type_theme
        if not cid[7:10] == 'PCS':
            platform = ps3
    elif platform_id == 2147483648 or platform_id == 2149580800 or platform_id == 2283798528 or platform_id == 2155872256:
        platform = ps3
        pkg_type = type_game_dlc
    elif platform_id == 4161798144 or platform_id == 1880096768 or platform_id == 4027580416: # (or platform_id == 2014314496 ?)
        platform = psp
        pkg_type = type_game_dlc
        if cid[7:8] == 'B':
            platform = ps3
    else:
        platform = ps3
        pkg_type = type_game_dlc
        if cid[7:8] == 'U':
            platform = psp

    if cid[7:10] == 'PCS':
        platform = psv

    if package_sub_type == 'MISC_AVATAR':
        platform = ps3
        pkg_type = type_avatar

    #Special CIDs
    if cid == 'EP9000-PCSF00178_00-SOULENTITLEMENT1':
        platform = ps3
    if cid == 'UP1082-NPUB90491_00-SPLITSECONDDEM21':
        platform = ps3
    if cid == 'JP9002-NPJW90014_00-0000000000000003': # platform_id == 2014314496
        platform = psp
        pkg_type = type_theme
    if cid[20:35] == 'KAGURAPLUSTHEME':
        platform = ps3
        pkg_type = type_theme

    return platform, pkg_type


def is_pkg_missing(pkg_filename, pkg_db):
    if pkg_filename in pkg_db:
        return False
    else:
        return True


def is_license_missing(platform, drm_type, cid, license_db):
    if platform == psp:
        return False
    if drm_type == 3 or drm_type == 13:
        return False
    if cid in license_db:
        return False
    else:
        return True


class PlatformData:
    def __init__(self, platform):
        self.platform = platform
        self.item_count = 0
        self.results = []
        self.submission_json = {'items': []}

        if platform == psv:
            self.csv_header_license = '*Missing zRIF'
            self.plat_name = 'PS Vita'
        elif platform == ps3:
            self.csv_header_license = '*Missing RAP'
            self.plat_name = 'PS3'
        elif platform == psp:
            self.csv_header_license = '*Missing RAP'
            self.plat_name = 'PSP'

        if args.csv:
            self.output_results_name = platform + '_results.csv'
        else:
            self.output_results_name = platform + '_results.tsv'

        self.output_json_name = platform + '_submission.json'

    def add_new_item(self, p):
        if self.item_count == 0:
            if args.debug:
                csv_header = ['Item No.', 'Content Name', 'Platform', '*Missing PKG', self.csv_header_license,
                              'PS Plus', 'Content ID', 'Size', 'Date', 'Base Game',
                              'titleid', 'platform_id', 'product_id', 'drm_type', 'package_sub_type', 'pkg']
            else:
                csv_header = ['Item No.', 'Content Name', 'Platform', '*Missing PKG', self.csv_header_license,
                              'PS Plus', 'Content ID', 'Size', 'Date', 'Base Game']
            self.results.append(csv_header)

        if args.debug:
            newrow = [self.item_count+1, p['name'], self.plat_name, p['missing_pkg'], p['missing_license'],
                      p['psplus'], p['cid'], p['size'], p['active_date'][0:10], p['base_game'],
                      p['cid'][7:16], p['platform_id'], p['product_id'], p['drm_type'], p['package_sub_type'], p['pkg']]
        else:
            newrow = [self.item_count+1, p['name'], self.plat_name, p['missing_pkg'], p['missing_license'], 
                      p['psplus'], p['cid'], p['size'], p['active_date'][0:10], p['base_game']]
                      
        self.results.append(newrow)
        
        new_item = {'platform': self.plat_name, 'name': p['name'], 'pkg': p['pkg'], 'id': p['cid'],
                    'size': p['size'], 'baseGame': p['base_game'], 'productID': p['product_id'], 'url': ''}
        
        self.submission_json['items'].append(new_item)
        self.item_count += 1

    def output(self):
        dist_dir = './output/'
        os.makedirs(dist_dir, exist_ok=True)

        if not self.item_count == 0:
            with open(dist_dir+self.output_results_name, 'w', encoding='utf-8', newline='') as f:
                if args.csv:
                    writer = csv.writer(f, delimiter=',')
                else:
                    writer = csv.writer(f, delimiter='\t')
                writer.writerows(self.results)
            print(f'{dist_dir}{self.output_results_name:.<24s}done')
    
            with open(dist_dir+self.output_json_name, 'w', encoding='utf-8') as f:
                json.dump(self.submission_json, f, ensure_ascii=False, indent=4)
            print(f'{dist_dir}{self.output_json_name:.<24s}done')


def main():
    try:
        with open(args.input_file, 'rb') as f:
            entitlement_json = json.loads(f.read())
        data_length = len(entitlement_json['entitlements'])
    except:
         print('Error!...Invalid json file.', '\n')
         input('Press Enter to exit.')
         sys.exit(1)

    dpath = os.path.dirname(os.path.abspath(sys.argv[0]))
    os.chdir(dpath)

    print('Downloading database files', end='', flush=True)
    try:
        download_db()
    except:
        pass
    print('.......done')

    try:
        pkg_db, license_db = load_db()
    except:
         print('Error!...Could not open the database files.', '\n')
         input('Press Enter to exit.')
         sys.exit(1)

    print(f'Checking {data_length:>4d} items', end='', flush=True)
    psv_data = PlatformData(psv)
    ps3_data = PlatformData(ps3)
    psp_data = PlatformData(psp)
    for entitlement in reversed(entitlement_json['entitlements']):
        p = get_params(entitlement)
        if not p:
            continue

        p['platform'], p['pkg_type'] = get_platform(p['platform_id'], p['cid'], p['package_sub_type'])

        if is_pkg_missing(p['pkg_filename'], pkg_db):
            p['missing_pkg'] = 'Yes'
        else:
            p['missing_pkg'] = ''

        if is_license_missing(p['platform'], p['drm_type'], p['cid'], license_db):
            p['missing_license'] = 'Yes'
        else:
            p['missing_license'] = ''

        if p['missing_pkg'] or p['missing_license'] or args.debug:
            if p['platform'] == psv:
                psv_data.add_new_item(p)
            elif p['platform'] == ps3:
                ps3_data.add_new_item(p)
            elif p['platform'] == psp:
                psp_data.add_new_item(p)

        if args.debug:
            print(p['pkg'])

    print('..............done', '\n')

    if psv_data.item_count == 0 and ps3_data.item_count == 0 and psp_data.item_count == 0:
        print('All items are already in the database.', '\n')
    else:
        try:
            psv_data.output()
            ps3_data.output()
            psp_data.output()
        except:
            print('Error!...Could not create the result files.', '\n')
            input('Press Enter to exit.')
            sys.exit(1)

        if not args.debug:
            found = psv_data.item_count + ps3_data.item_count + psp_data.item_count
            print(f'Found {found} items in total!', '\n')
            print('* Please check "xxx_results.tsv" and create missing NoNpDrm/RAP licenses.')
            print('* Then submit "xxx_submission.json" along with the created licenses (zipped file) on')
            print('* the NPS Contribution page. [ https://nopaystation.com/contribute/batch ]')
            print('*')
            print('* For more details, see the contribution FAQ. [ https://nopaystation.com/faq ] \n')

    input('Press Enter to exit.')
    sys.exit(0)


if __name__ == '__main__':
    main()