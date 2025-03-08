"""
メインスクリプト - データ取得処理を実行します
このスクリプトは株価データの取得、分析、シグナル抽出を行うメインエントリーポイントです
"""
import os
import sys
import argparse
import logging
import importlib
from typing import List

# モジュールのパスをPythonパスに追加
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 自作モジュールのインポート
import config  # 設定値を管理するモジュール
from data_loader import setup_logger, load_company_list  # ロガー設定と企業リスト読み込み関数
from stock_fetcher import fetch_stock_data  # 株価データを取得する関数
from technical_indicators import calculate_signals  # テクニカル指標を計算する関数
from extract_signals import extract_signals  # 売買シグナルを抽出する関数

def main():
    """
    メイン処理
    コマンドライン引数の解析、企業リストの読み込み、株価データの取得、
    テクニカル指標の計算、売買シグナルの抽出までの一連の処理を実行します
    """
    # コマンドライン引数の解析 - テストモードのフラグを受け取る
    parser = argparse.ArgumentParser(description='株価データ取得ツール')
    parser.add_argument('--test', action='store_true', help='テストモードで実行')
    args = parser.parse_args()
    
    # テストモードかどうかのフラグを保存
    is_test_mode = args.test
    
    # ロガーの設定（テストモードに応じた設定）
    # テストモードではより詳細なログレベルや別のログファイルを使用する可能性がある
    logger = setup_logger(is_test_mode)
    logger.info("=== 株価データ取得ツール 開始 ===")
    logger.info(f"実行モード: {'テスト' if is_test_mode else '通常'}")
    
    try:
        # 企業リストの読み込み
        # テストモードの場合は限定された企業リストを読み込む
        tickers = load_company_list(is_test_mode)
        
        # 企業リストが空の場合はエラーを記録して処理を終了
        if not tickers:
            logger.error("企業リストが空です。処理を終了します。")
            return 1
        
        # 株価データの取得
        # configモジュールから設定値（バッチサイズ、期間など）を取得して実行
        stock_data = fetch_stock_data(tickers, is_test_mode=is_test_mode)
        
        # テクニカル指標の計算処理を開始
        logger.info("テクニカル指標の計算を開始します...")
        
        try:
            # 各銘柄に対してテクニカル指標（移動平均、RSI、MACDなど）を計算
            signal_results = calculate_signals(tickers, is_test_mode)
            logger.info("テクニカル指標の計算が完了しました。")
            
            # 計算されたテクニカル指標に基づいて売買シグナルを抽出
            logger.info("Buy/Sellシグナルの抽出を開始します...")
            extract_success = extract_signals(is_test_mode)
            
            # シグナル抽出の結果をログに記録
            if extract_success:
                logger.info("Buy/Sellシグナルの抽出が完了しました。")
            else:
                logger.error("Buy/Sellシグナルの抽出中にエラーが発生しました。")
            
        except Exception as e:
            # テクニカル指標計算中のエラーハンドリング
            logger.error(f"テクニカル指標の計算中にエラーが発生しました: {str(e)}")
        
        # 全処理の完了を記録して正常終了
        logger.info("=== 株価データ取得ツール 終了 ===")
        return 0
        
    except Exception as e:
        # メイン処理全体での例外をキャッチしてログに記録
        logger.error(f"予期せぬエラーが発生しました: {str(e)}")
        return 1

# スクリプトが直接実行された場合のみmain関数を実行
# 戻り値をsys.exitに渡してプロセスの終了コードを設定
if __name__ == "__main__":
    sys.exit(main())