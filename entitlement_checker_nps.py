#!/usr/bin/env python3

import csv
import json
import sys
import os
import urllib.request

extract_all = False

psv = 'psv'
ps3 = 'ps3'
psp = 'psp'

type_game = 'GAME'
type_dlc = 'DLC'
type_theme = 'THEME'
type_avatar = 'AVATAR'
type_game_dlc = 'GAME/DLC'

def download_file(filename):
    repo_url = 'https://raw.githubusercontent.com/1jtp8sobiu/entitlement_checker_nps/master/db_files/'
    dist_dir = './db_files/'
    os.makedirs(dist_dir, exist_ok=True)
    urllib.request.urlretrieve(repo_url+filename, dist_dir+filename)

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
    if cid == 'EP9000-PCSF00178_00-SOULENTITLEMENT1' or cid == 'UP1082-NPUB90491_00-SPLITSECONDDEM21':
        platform = ps3
    elif cid == 'JP9002-NPJW90014_00-0000000000000003': # platform_id == 2014314496
        platform = psp
        pkg_type = type_theme
    elif cid[20:35] == 'KAGURAPLUSTHEME':
        platform = ps3
        pkg_type = type_theme

    return platform, pkg_type

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

        self.output_results_name = platform + '_results.tsv'
        self.output_json_name = platform + '_submission.json'

    def add_new_item(self, pkg, active_date, cid, name, size, drm_type, platform_id, base_game, product_id, package_sub_type, missing_pkg, missing_license, psplus):
            if self.item_count == 0:
                csv_header = ['Item No.', 'Content Name', 'Platform', '*Missing PKG', self.csv_header_license, 'PS Plus', 'Content ID', 'Size', 'Date', 'Base Game']
                if extract_all:
                    csv_header = ['Item No.', 'Content Name', 'Platform', '*Missing PKG', self.csv_header_license, 'PS Plus', 'Content ID', 'Size', 'Date', 'Base Game', 'titleid', 'platform_id', 'product_id', 'drm_type', 'package_sub_type', 'pkg']
                self.results.append(csv_header)

            newrow = [self.item_count+1, name, self.plat_name, missing_pkg, missing_license, psplus, cid, size, active_date[0:10], base_game]
            if extract_all:
                newrow = [self.item_count+1, name, self.plat_name, missing_pkg, missing_license, psplus, cid, size, active_date[0:10], base_game, cid[7:16], platform_id, product_id, drm_type, package_sub_type, pkg]
            self.results.append(newrow)
            new_item = {'platform': self.plat_name, 'name': name, 'pkg': pkg, 'id': cid, 'size': size, 'baseGame': base_game, 'productID': product_id, 'url': ''}
            self.submission_json['items'].append(new_item)
            self.item_count += 1

    def output(self):
        dist_dir = './output/'
        os.makedirs(dist_dir, exist_ok=True)

        if not self.item_count == 0:
            with open(dist_dir+self.output_results_name, 'w', encoding='utf-8', newline='') as f:
                writer = csv.writer(f, delimiter='\t')
                writer.writerows(self.results)
            print(f'{dist_dir}{self.output_results_name:.<24s}done')
    
            with open(dist_dir+self.output_json_name, 'w', encoding='utf-8') as f:
                json.dump(self.submission_json, f, ensure_ascii=False, indent=4)
            print(f'{dist_dir}{self.output_json_name:.<24s}done')

def main():
    dpath = os.path.dirname(sys.argv[0]) # Get absolute path for PyInstaller
    os.chdir(dpath)

    try:
        with open(sys.argv[1], 'rb') as f:
            entitlement_json = json.loads(f.read())
        item_count_all = len(entitlement_json['entitlements'])
    except:
         print('Error!...Invalid json file.\n')
         input('Press Enter to exit.')
         sys.exit()

    print('Downloading db files...')
    try:
        download_file('pkg.tsv')
        download_file('pkg_exception.tsv')
        download_file('zrif.tsv')
        download_file('rap.tsv')
        download_file('last_updated.txt')
    except:
        pass

    try:
        with open('./db_files/pkg.tsv', newline='') as f:
            pkg_list = f.read()
        with open('./db_files/pkg_exception.tsv', newline='') as f:
            pkg_exception_list = f.read()
        with open('./db_files/zrif.tsv', newline='') as f:
            license_list = f.read()
        with open('./db_files/rap.tsv', newline='') as f:
            license_list += f.read()
    except:
         print('Error!...Couldn\'t open files.\n')
         input('Press Enter to exit.')
         sys.exit()

    psv_data = PlatformData(psv)
    ps3_data = PlatformData(ps3)
    psp_data = PlatformData(psp)

    print(f'Checking {item_count_all} items...')
    for entitlement in reversed(entitlement_json['entitlements']):
        try:
            pkg = entitlement['drm_def']['drmContents'][0]['contentUrl']
            pkg_domain = pkg.split('/')[2]
            pkg_filename = pkg.split('/')[-1]
        except:
            pkg = False
            pkg_domain = False
            pkg_filename = False

        if not (pkg_domain == 'ares.dl.playstation.net' or pkg_domain == 'zeus.dl.playstation.net' or pkg_domain == 'hfs.dl.playstation.net'):
            continue

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
            package_sub_type = False

        platform = get_platform(platform_id, cid, package_sub_type)[0]
        pkg_type = get_platform(platform_id, cid, package_sub_type)[1]

        try:
            psplus = entitlement['drm_def']['expiration']
            psplus = 'Yes'
        except:
            psplus = ''

        if pkg_filename not in pkg_list and pkg_filename not in pkg_exception_list:
            missing_pkg = 'Yes'
        else:
            missing_pkg = ''
        if (platform == psv or platform == ps3) and not (drm_type == 3 or drm_type == 13) and cid not in license_list:
            missing_license = 'Yes'
        else:
            missing_license = ''
            
        if extract_all:
            pass
        else:
            if missing_pkg == '' and missing_license == '':
                continue

        item_data = (pkg, active_date, cid, name, size, drm_type, platform_id, base_game, product_id, package_sub_type, missing_pkg, missing_license, psplus)
        if platform == psv:
            psv_data.add_new_item(*item_data)
        elif platform == ps3:
            ps3_data.add_new_item(*item_data)
        elif platform == psp:
            psp_data.add_new_item(*item_data)

    print('Done.\n')

    if psv_data.item_count == 0 and ps3_data.item_count == 0 and psp_data.item_count == 0:
        print('All items are already in the DB.\n')
    else:
        try:
            psv_data.output()
            ps3_data.output()
            psp_data.output()
        except:
            print('Error!...Couldn\'t create result files\n')
            input('Press Enter to exit.')
            sys.exit()

        print()
        print('Please check "xxx_results.tsv" and create missing NoNpDrm/RAP licenses.')
        print('Then submit "xxx_submission.json" along with the created licenses (zipped file) to the NPS DB.')
        print('For more details, see the contribution FAQ. https://nopaystation.com/faq \n')

    input('Press Enter to exit.')
    sys.exit()

if __name__ == '__main__':
    main()