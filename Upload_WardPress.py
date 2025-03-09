"""
株価分析結果をWordPressに自動投稿するスクリプト

このスクリプトは、株価シグナル分析の結果をWordPressサイトに自動投稿します。
主な機能：
1. 買いシグナルと売りシグナルのCSVファイルを読み込み
2. CSVデータをHTML形式のテーブルに変換
3. WordPress REST APIを使用して記事を投稿
4. 記事内に展開可能なブロックとして表を表示
"""
import pandas as pd
import requests
from requests.auth import HTTPBasicAuth
from datetime import datetime, timedelta

# WordPressサイトの接続情報を設定
WP_SITE_URL = "https://www.takstorage.site/"  # WordPressサイトのURL
WP_API_ENDPOINT = f"{WP_SITE_URL}/wp-json/wp/v2/posts"  # WordPress REST API 投稿用エンドポイント
WP_USERNAME = "tak.note7120@gmail.com"  # WordPressの管理者ユーザー名（メールアドレス）
WP_APP_PASSWORD = "GNrk aQ3d 7GWu p1fw dCfM pAGH"  # WordPress アプリケーションパスワード（セキュリティ向上のため通常のパスワードではなくアプリパスワードを使用）

# 今日の日付と昨日の日付を取得（昨日の株価データを投稿するため）
current_date = datetime.now()
yesterday_date = (current_date - timedelta(days=1)).strftime("%Y/%m/%d")  # YYYY/MM/DD形式

# 投稿の冒頭部分のテキスト（HTMLタグ含む）
# 投稿の説明文と銘柄コードの解説を含む
intro_text = """
<p>{yesterday_date}終わり時点での情報です。</p>
<p>Pythonを使用して自動でデータ収集&演算を行っています。</p>
<p>銘柄名に付いているアルファベットで市場を表しています。</p>
<div class="graybox">
<p>P: プライム市場の銘柄</p>
<p>S: スタンダード市場の銘柄</p>
<p>G: グロース市場の銘柄</p>
</div>
<p></p>
<p>シグナルは下記の条件で導出しています。</p>
[st-mybox title="買いシグナルの条件" webicon="st-svg-check-circle" color="#03A9F4" bordercolor="#B3E5FC" bgcolor="#E1F5FE" borderwidth="2" borderradius="5" titleweight="bold"]
<ol>
<li>MACDがMACDシグナルを上回っている</li>
<li>RSI短期がRSI長期を上回っている</li>
<li>RSI長期が40以下</li>
</ol>
[/st-mybox]
[st-mybox title="売りシグナルの条件" webicon="st-svg-check-circle" color="#03A9F4" bordercolor="#B3E5FC" bgcolor="#E1F5FE" borderwidth="2" borderradius="5" titleweight="bold"]
<ol>
<li>MACDがMACDシグナルを下回っている</li>
<li>RSI短期がRSI長期を下回っている</li>
<li>RSI長期が60以上</li>
</ol>
[/st-mybox]
<p></p>
""".format(yesterday_date=yesterday_date)

def read_csv_to_html_table(csv_file_path, decimal_places=2):
    """
    CSVファイルを読み込み、スタイリングされたHTML表に変換します
    
    Args:
        csv_file_path (str): 読み込むCSVファイルのパス
        decimal_places (int): 小数点以下の表示桁数（デフォルト: 2桁）
        
    Returns:
        str: スタイル適用済みのHTML表（スクロール可能なコンテナ内）
    """
    # CSVファイルをpandasデータフレームとして読み込み
    df = pd.read_csv(csv_file_path)

    # 小数点以下の桁数を統一（float型の列のみ適用）
    # 例: 終値などの小数点以下を指定桁数に揃える
    for col in df.select_dtypes(include=['float']):
        df[col] = df[col].round(decimal_places)

    # DataFrame を HTML テーブルに変換
    # index=False: インデックスは表示しない
    # border=1: テーブル境界線を表示
    # escape=False: HTML特殊文字をエスケープしない（HTMLタグを使用可能に）
    df_html = df.to_html(index=False, border=1, escape=False)

    # 銘柄名（Name列）が長い場合でもテーブルレイアウトを崩さないようにスタイル適用
    # 列幅の最大値を制限し、長いテキストは折り返す
    df_html = df_html.replace('<th>', '<th style="max-width:800px; white-space:nowrap; overflow:hidden;">')
    df_html = df_html.replace('<td>', '<td style="max-width:800px; word-wrap:break-word;">')

    # テーブルをスクロール可能なdivコンテナでラップ
    # コンテンツが大きくても表示領域を固定できる
    styled_table = f"""
    <div class="scroll-box">
        {df_html}
    </div>
    """
    return styled_table

def post_to_wordpress(title, post_content):
    """
    WordPressに投稿記事を送信します
    
    Args:
        title (str): 投稿のタイトル
        post_content (str): 投稿の本文（HTMLフォーマット）
        
    Returns:
        None: 結果はコンソールに出力されます
    """
    # 投稿データの構成
    post_data = {
        "title": title,             # 記事タイトル
        "content": post_content,    # 記事本文（HTML）
        "status": "publish",        # 公開ステータス（下書き="draft"）
        "categories": [22],         # カテゴリーID（22=株価情報カテゴリー）
        "tags": [19],               # タグID（19=株価情報タグ）
        "featured_media": 233       # アイキャッチ画像ID
    }
    
    # WordPress REST APIにリクエストを送信
    # HTTPBasicAuth: ユーザー名とアプリパスワードで認証
    response = requests.post(
        WP_API_ENDPOINT,
        json=post_data,
        auth=HTTPBasicAuth(WP_USERNAME, WP_APP_PASSWORD)
    )
    
    # レスポンスを確認して結果をコンソールに表示
    if response.status_code == 201:  # 201 Created = 投稿成功
        print("投稿が成功しました:", response.json()["link"])
    else:
        print("投稿に失敗しました:", response.status_code, response.text)

def main():
    """
    メイン処理：CSVファイルの読み込み、HTML変換、WordPress投稿を実行
    """
    # 読み込むCSVファイルのパス
    signal_buy_csv_file_path = "C:\\Users\\mount\\Git\\StockSignal\\Result\\signal_result_buy.csv"   # 買いシグナルCSV
    signal_sell_csv_file_path = "C:\\Users\\mount\\Git\\StockSignal\\Result\\signal_result_sell.csv" # 売りシグナルCSV
    
    # 各CSVファイルを読み込んで、銘柄コード(Ticker)列で昇順ソートして再保存
    # 表示時に銘柄コードでソートされた状態にするため
    for file_path in [signal_buy_csv_file_path, signal_sell_csv_file_path]:
        df = pd.read_csv(file_path, encoding='utf-8')    # CSVファイルを読み込み
        df_sorted = df.sort_values(by='Ticker')          # Ticker列で昇順ソート
        df_sorted.to_csv(file_path, index=False, encoding='utf-8')  # ソート結果を上書き保存
    
    # CSVデータをHTML表に変換
    html_table_buy = read_csv_to_html_table(signal_buy_csv_file_path)   # 買いシグナルテーブル
    html_table_sell = read_csv_to_html_table(signal_sell_csv_file_path) # 売りシグナルテーブル
    
    # 投稿のタイトルと内容を作成
    post_title = "売買シグナル_{yesterday_date}".format(yesterday_date=yesterday_date)  # 投稿タイトル
    
    # 投稿本文のHTML構成
    # WordPressテーマ「AFFINGER」用のスライドボックスブロックを使用
    # 初期状態では折りたたまれており、クリックで展開される
    post_content = f"""
        {intro_text}
        <h2>売買シグナル</h2>
        <p>前述の条件でフィルタリングした銘柄を抽出しています。</p>
        <h3>買いシグナル銘柄</h3>
        <p><!-- wp:st-blocks/st-slidebox --></p>
        <div class="wp-block-st-blocks-st-slidebox st-slidebox-c is-collapsed has-st-toggle-icon is-st-toggle-position-left is-st-toggle-icon-position-left" data-st-slidebox="">
        <p class="st-btn-open" data-st-slidebox-toggle=""><i class="st-fa st-svg-plus-thin" data-st-slidebox-icon="" data-st-slidebox-icon-collapsed="st-svg-plus-thin" data-st-slidebox-icon-expanded="st-svg-minus-thin" aria-hidden=""></i><span class="st-slidebox-btn-text" data-st-slidebox-text="" data-st-slidebox-text-collapsed="クリックして展開" data-st-slidebox-text-expanded="閉じる">クリックして下さい</span></p>
        <div class="st-slidebox" data-st-slidebox-content="">
        <div class="scroll-box">
        買いシグナルテーブル
        {html_table_buy}
        </div>
        </div>
        </div>
        <p><!-- /wp:st-blocks/st-slidebox --></p>
        
        <h3>売りシグナル銘柄</h3>
        <p><!-- wp:st-blocks/st-slidebox --></p>
        <div class="wp-block-st-blocks-st-slidebox st-slidebox-c is-collapsed has-st-toggle-icon is-st-toggle-position-left is-st-toggle-icon-position-left" data-st-slidebox="">
        <p class="st-btn-open" data-st-slidebox-toggle=""><i class="st-fa st-svg-plus-thin" data-st-slidebox-icon="" data-st-slidebox-icon-collapsed="st-svg-plus-thin" data-st-slidebox-icon-expanded="st-svg-minus-thin" aria-hidden=""></i><span class="st-slidebox-btn-text" data-st-slidebox-text="" data-st-slidebox-text-collapsed="クリックして展開" data-st-slidebox-text-expanded="閉じる">クリックして下さい</span></p>
        <div class="st-slidebox" data-st-slidebox-content="">
        <div class="scroll-box">
        売りシグナルテーブル
        {html_table_sell}
        </div>
        </div>
        </div>
        <p><!-- /wp:st-blocks/st-slidebox --></p>
        
        """
    
    # WordPressに投稿を送信
    post_to_wordpress(post_title, post_content)
    # print(post_content)  # デバッグ用：投稿内容をコンソールに出力（必要に応じてコメント解除）


# スクリプトが直接実行された場合の処理
if __name__ == "__main__":
    main()  # メイン処理を実行