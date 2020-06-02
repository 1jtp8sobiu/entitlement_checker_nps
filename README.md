# PSN Entitlement Checker for NPS

このスクリプトでは自分のPSNアカウント内にあるコンテンツ情報をチェックし、まだNPSに登録されていないコンテンツのみを抽出することができます。
結果はJSONファイルとして出力され、そのままNPSサイトにて投稿できます。

このスクリプトは、主に次のような場合に役に立つかも知れません。
- 自分のアカウント内にまだNPSに登録されていないコンテンツがあるかどうか確認したい場合。
- アカウント内のどのコンテンツのfake licenseを作成すべきなのか分からない場合。
- NPS投稿ページでの検証時間を最少減に抑えたい場合。

## 使い方
1. [Pythonスクリプト](https://raw.githubusercontent.com/1jtp8sobiu/entitlement_checker_nps/master/entitlement_checker_nps.py) または [Windowsバイナリ](https://raw.githubusercontent.com/1jtp8sobiu/entitlement_checker_nps/master/entitlement_checker_nps.exe)をダウンロードします。
2. [PS Store](https://store.playstation.com/)にアクセスし、サインインします。
3. プロフィール画像等が表示され、ページが完全に読み込まれるまで待機します。
4. 次のページからPSNアカウントに存在するコンテンツ情報をダウンロードします (右クリックして保存)。  
https://store.playstation.com/kamaji/api/chihiro/00_09_000/gateway/store/v1/users/me/internal_entitlements?size=10000&fields=game_meta,drm_def
5. 次のようにコマンドをタイプします。  
`>python entitlement_checker_nps.py internal_entitlements.json`  
もしくは `internal_entitlements.json` を `entitlement_checker_nps.exe` へとドラッグ&ドロップします。
6. 'output'フォルダに 'xxx_submission_xxx.json' と 'xxx_results.tsv' が作成されたことを確認します。  
Note: 既に全てのコンテンツがデータベースに存在する場合はその旨が表示されます。
7. 'xxx_results.tsv' を確認し、不足しているNoNpDrm fake licenseまたはRAP ファイルを作成します。
8. 作成したlicenseファイルをzipファイルとして纏めて、'submission_xxx.json' と共に[投稿ページ](https://nopaystation.com/contribute/batch)から投稿してください。

**Notes:**
- 適切な NoNpDrm fake licenseファイルの作成方法は[Contribution FAQ](https://nopaystation.com/faq)を参照してください。  
'Creating NoNpDRM licenses for PSV Games and DLCs' セクション参照。ただし、最下部の 'Creating zRIFs' セクションは実行する必要はありません。
- NoNpDrm fake licenseを作成する際は、'FAST method' を利用することを推奨します。
- コンテンツチェックの簡略化のために、このスクリプトではレポジトリから必要なファイルをダウンロードして比較を行っています。
- **このスクリプトでは、現在NPSサイト上で承認待ちのアイテムの場合は、それをチェックできません。そのため結果に重複して表示される場合があります。**

## テスト環境
Windows 10 x64 Version 1903  
Python 3.7
