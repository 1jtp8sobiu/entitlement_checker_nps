\#[日本語](https://github.com/1jtp8sobiu/entitlement_checker_nps#%E6%97%A5%E6%9C%AC%E8%AA%9E)

# PSN Entitlement Checker for NPS
This script can check the entitlement information in your PSN account and extract only items that have not yet been contributed to NPS.
The result will be output as a JSON file and a TSV file, and the JSON file can be submitted on the NPS site as it is.  
  
This script may be useful mainly in the following cases:
- If you want to check if there are items in your account that are not yet contributed to NPS.
- If you don't know which items in your account to create fake licenses for.
- If you want to minimize the validating time on the NPS contribution page.

## How to use
1. Download a [Python script](https://raw.githubusercontent.com/1jtp8sobiu/entitlement_checker_nps/master/entitlement_checker_nps.py) or [Windows binary](https://raw.githubusercontent.com/1jtp8sobiu/entitlement_checker_nps/master/entitlement_checker_nps.exe) (right click to save).
2. Go to the PS Store `https://store.playstation.com/` and sign in.
3. Wait until your profile picture is displayed and the page is completely loaded.
4. Download the entitlement information of your PSN account from the next link (right click to save).  
https://store.playstation.com/kamaji/api/chihiro/00_09_000/gateway/store/v1/users/me/internal_entitlements?size=10000&fields=game_meta,drm_def
5. Type this command:  
`>python entitlement_checker_nps.py internal_entitlements.json`  
Or, drag and drop the `internal_entitlements.json` to `entitlement_checker_nps.exe`.
6. Make sure that 'xxx_submission.json' and 'xxx_results.tsv' have been created in the 'output' folder.  
Note: If all the content already exists in the database, it will be displayed.
7. Check the 'xxx_results.tsv' and create missing NoNpDrm fake licenses/RAP files.
8. Zip the created license files and submit it along with the 'xxx_submission.json' on [the contribution page](https://nopaystation.com/contribute/batch).

**Notes:**
- Please refer to the [Contribution FAQ](https://nopaystation.com/faq) on how to create proper NoNpDrm fake licenses.  
See 'Creating NoNpDRM licenses for PSV Games and DLCs:' section. However, the bottom 'Creating zRIFs' section is not necessary to do.
- I recommend using the 'Fast method' to create NoNpDrm fake license.
- Please do not submit legitimate license files tied with your account. Proper NoNpDrm fake licenses can be found in the 'ux0:nonpdrm' folder.
- To simplify the content check, this script downloads the required files from this repository and compares with them.
- **Keep in mind that this script cannot check items that are currently pending approval on the NPS site. Therefore, it may be displayed in duplicate in the result file.**

## Tested on
Windows 10 x64 Version 1903  
Python 3.7

## 日本語
このスクリプトでは自分のPSNアカウント内にあるコンテンツ情報をチェックし、まだNPSに登録されていないコンテンツのみを抽出することができます。
結果はJSONファイルおよびTSVファイルとして出力され、JSONファイルはそのままNPSサイトにて投稿できます。

このスクリプトは、主に次のような場合に役に立つかも知れません。
- 自分のアカウント内にまだNPSに登録されていないコンテンツがあるかどうか確認したい場合。
- アカウント内のどのコンテンツのfake licenseを作成すべきなのか分からない場合。
- NPS投稿ページでの検証時間を最小限に抑えたい場合。

## 使い方
1. [Pythonスクリプト](https://raw.githubusercontent.com/1jtp8sobiu/entitlement_checker_nps/master/entitlement_checker_nps.py) または [Windowsバイナリ](https://raw.githubusercontent.com/1jtp8sobiu/entitlement_checker_nps/master/entitlement_checker_nps.exe)をダウンロードします (右クリックして保存)。
2. PS Store `https://store.playstation.com/` にアクセスし、サインインします。
3. プロフィール画像等が表示され、ページが完全に読み込まれるまで待機します。
4. 次のページからPSNアカウントに存在するコンテンツ情報をダウンロードします (右クリックして保存)。  
https://store.playstation.com/kamaji/api/chihiro/00_09_000/gateway/store/v1/users/me/internal_entitlements?size=10000&fields=game_meta,drm_def
5. 次のようにコマンドをタイプします。  
`>python entitlement_checker_nps.py internal_entitlements.json`  
もしくは `internal_entitlements.json` を `entitlement_checker_nps.exe` へとドラッグ&ドロップします。
6. 'output'フォルダに 'xxx_submission.json' と 'xxx_results.tsv' が作成されたことを確認します。  
Note: 既に全てのコンテンツがデータベースに存在する場合はその旨が表示されます。
7. 'xxx_results.tsv' を確認し、不足しているNoNpDrm fake licenseまたはRAP ファイルを作成します。
8. 作成したlicenseファイルをzipファイルとして纏めて、'xxx_submission.json' と共に[投稿ページ](https://nopaystation.com/contribute/batch)から投稿してください。

**Notes:**
- 適切な NoNpDrm fake licenseの作成方法は[Contribution FAQ](https://nopaystation.com/faq)を参照してください。  
'Creating NoNpDRM licenses for PSV Games and DLCs' セクション参照。ただし、最下部の 'Creating zRIFs' セクションは実行する必要はありません。
- NoNpDrm fake licenseを作成する際は、'FAST method' を利用することを推奨します。
- 各自のアカウントに紐付いた正規のlicenseファイルをデータベースに投稿しないようにしてください。適切なNoNpDrm fake licenseは 'ux0:nonpdrm'フォルダ内にあります。
- コンテンツチェックの簡略化のために、このスクリプトではレポジトリから必要なファイルをダウンロードして比較を行っています。
- **このスクリプトでは、現在NPSサイト上で承認待ちのアイテムの場合は、それをチェックできません。そのため結果に重複して表示される場合があります。**

## テスト環境
Windows 10 x64 Version 1903  
Python 3.7
