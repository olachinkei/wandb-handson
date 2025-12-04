"""
===========================================
ART-E Email Search Agent - ユーティリティモジュール
===========================================

このモジュールには以下が含まれます：
- データモデル（Email, Scenario, SearchResult, FinalAnswer）
- SQLiteデータベース操作関数
- メール検索・読み込み関数
- シナリオ読み込み関数
"""

import os
import random
import sqlite3
from dataclasses import asdict, dataclass
from datetime import datetime
from typing import List, Literal, Optional

from datasets import Dataset, Features, Sequence, Value, load_dataset
from pydantic import BaseModel
from tqdm import tqdm


# ===========================================
# データモデル定義
# ===========================================

class Email(BaseModel):
    """
    メールデータを表すモデル
    
    Attributes:
        message_id: メールの一意識別子
        date: 送信日時（ISO 8601形式）
        subject: 件名
        from_address: 送信者アドレス
        to_addresses: 宛先アドレスリスト
        cc_addresses: CCアドレスリスト
        bcc_addresses: BCCアドレスリスト
        body: 本文
        file_name: ファイル名
    """
    message_id: str
    date: str  # ISO 8601形式 'YYYY-MM-DD HH:MM:SS'
    subject: Optional[str] = None
    from_address: Optional[str] = None
    to_addresses: List[str] = []
    cc_addresses: List[str] = []
    bcc_addresses: List[str] = []
    body: Optional[str] = None
    file_name: Optional[str] = None


class Scenario(BaseModel):
    """
    トレーニング/テスト用シナリオを表すモデル
    
    Attributes:
        id: シナリオID
        question: ユーザーからの質問
        answer: 期待される回答
        message_ids: 参照すべきメールのID
        how_realistic: リアリティスコア（0-1）
        inbox_address: 検索対象のメールアドレス
        query_date: 質問日付
        split: データセット分割（train/test）
    """
    id: int
    question: str
    answer: str
    message_ids: List[str]
    how_realistic: float
    inbox_address: str
    query_date: str
    split: Literal["train", "test"]


@dataclass
class SearchResult:
    """
    メール検索結果を表すデータクラス
    
    Attributes:
        message_id: メールID
        snippet: 検索結果のスニペット（ハイライト付き）
    """
    message_id: str
    snippet: str


class FinalAnswer(BaseModel):
    """
    エージェントの最終回答を表すモデル
    
    Attributes:
        answer: 回答テキスト
        source_ids: 回答の根拠となったメールID
    """
    answer: str
    source_ids: list[str]


# ===========================================
# データベース設定
# ===========================================

# データベースファイルのパス
DB_PATH = "./enron_emails.db"

# Hugging Faceデータセットのリポジトリ
EMAIL_DATASET_REPO_ID = "corbt/enron-emails"
SCENARIO_DATASET_REPO_ID = "corbt/enron_emails_sample_questions"

# グローバルデータベース接続（シングルトンパターン）
_db_conn = None


# ===========================================
# データベース作成・接続関数
# ===========================================

def create_email_database() -> sqlite3.Connection:
    """
    Hugging Faceデータセットからメールデータベースを作成
    
    Enronメールデータセット全体をダウンロードし、SQLiteデータベースに格納します。
    フルテキスト検索（FTS5）も設定されます。
    
    Returns:
        sqlite3.Connection: データベース接続オブジェクト
    """
    print("Hugging Faceデータセットからメールデータベースを作成中...")
    print("Enronメールデータセット全体をダウンロード・処理します（数分かかる場合があります）...")

    # ===========================================
    # データベーススキーマ定義
    # ===========================================
    SQL_CREATE_TABLES = """
    DROP TABLE IF EXISTS recipients;
    DROP TABLE IF EXISTS emails_fts;
    DROP TABLE IF EXISTS emails;

    -- メインのメールテーブル
    CREATE TABLE emails (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        message_id TEXT UNIQUE,
        subject TEXT,
        from_address TEXT,
        date TEXT,
        body TEXT,
        file_name TEXT
    );

    -- 受信者テーブル（to, cc, bccを格納）
    CREATE TABLE recipients (
        email_id TEXT,
        recipient_address TEXT,
        recipient_type TEXT
    );
    """

    # インデックスとFTS（フルテキスト検索）の設定
    SQL_CREATE_INDEXES_TRIGGERS = """
    -- 検索高速化のためのインデックス
    CREATE INDEX idx_emails_from ON emails(from_address);
    CREATE INDEX idx_emails_date ON emails(date);
    CREATE INDEX idx_emails_message_id ON emails(message_id);
    CREATE INDEX idx_recipients_address ON recipients(recipient_address);
    CREATE INDEX idx_recipients_type ON recipients(recipient_type);
    CREATE INDEX idx_recipients_email_id ON recipients(email_id);
    CREATE INDEX idx_recipients_address_email ON recipients(recipient_address, email_id);

    -- FTS5仮想テーブル（フルテキスト検索用）
    CREATE VIRTUAL TABLE emails_fts USING fts5(
        subject,
        body,
        content='emails',
        content_rowid='id'
    );

    -- FTSテーブルを自動同期するトリガー
    CREATE TRIGGER emails_ai AFTER INSERT ON emails BEGIN
        INSERT INTO emails_fts (rowid, subject, body)
        VALUES (new.id, new.subject, new.body);
    END;

    CREATE TRIGGER emails_ad AFTER DELETE ON emails BEGIN
        DELETE FROM emails_fts WHERE rowid=old.id;
    END;

    CREATE TRIGGER emails_au AFTER UPDATE ON emails BEGIN
        UPDATE emails_fts SET subject=new.subject, body=new.body WHERE rowid=old.id;
    END;
    """

    # データベース作成
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.executescript(SQL_CREATE_TABLES)
    conn.commit()

    # ===========================================
    # Hugging Faceからデータセットをロード
    # ===========================================
    print("メールデータセットをロード中...")
    expected_features = Features(
        {
            "message_id": Value("string"),
            "subject": Value("string"),
            "from": Value("string"),
            "to": Sequence(Value("string")),
            "cc": Sequence(Value("string")),
            "bcc": Sequence(Value("string")),
            "date": Value("timestamp[us]"),
            "body": Value("string"),
            "file_name": Value("string"),
        }
    )

    dataset = load_dataset(
        EMAIL_DATASET_REPO_ID, features=expected_features, split="train"
    )
    print(f"データセットには合計 {len(dataset)} 通のメールが含まれています")

    # ===========================================
    # データベースへのメール挿入
    # ===========================================
    print("全メールをデータベースに挿入中...")
    
    # パフォーマンス最適化設定
    conn.execute("PRAGMA synchronous = OFF;")
    conn.execute("PRAGMA journal_mode = MEMORY;")
    conn.execute("BEGIN TRANSACTION;")

    record_count = 0
    skipped_count = 0
    duplicate_count = 0
    processed_emails = set()  # 重複検出用

    for email_data in tqdm(dataset, desc="メール挿入中"):
        message_id = email_data["message_id"]
        subject = email_data["subject"]
        from_address = email_data["from"]
        date_obj: datetime = email_data["date"]
        body = email_data["body"]
        file_name = email_data["file_name"]
        to_list = [str(addr) for addr in email_data["to"] if addr]
        cc_list = [str(addr) for addr in email_data["cc"] if addr]
        bcc_list = [str(addr) for addr in email_data["bcc"] if addr]

        # ===========================================
        # フィルタリング条件
        # ===========================================
        total_recipients = len(to_list) + len(cc_list) + len(bcc_list)

        # 長すぎるメールをスキップ（5000文字以上）
        if len(body) > 5000:
            skipped_count += 1
            continue

        # 受信者が多すぎるメールをスキップ（30人以上）
        if total_recipients > 30:
            skipped_count += 1
            continue

        # 重複チェック（件名、本文、送信者の組み合わせで判定）
        email_key = (subject, body, from_address)
        if email_key in processed_emails:
            duplicate_count += 1
            continue
        else:
            processed_emails.add(email_key)

        date_str = date_obj.strftime("%Y-%m-%d %H:%M:%S")

        # メール挿入
        cursor.execute(
            """
            INSERT INTO emails (message_id, subject, from_address, date, body, file_name)
            VALUES (?, ?, ?, ?, ?, ?)
        """,
            (message_id, subject, from_address, date_str, body, file_name),
        )

        # 受信者を挿入
        recipient_data = []
        for addr in to_list:
            recipient_data.append((message_id, addr, "to"))
        for addr in cc_list:
            recipient_data.append((message_id, addr, "cc"))
        for addr in bcc_list:
            recipient_data.append((message_id, addr, "bcc"))

        if recipient_data:
            cursor.executemany(
                """
                INSERT INTO recipients (email_id, recipient_address, recipient_type)
                VALUES (?, ?, ?)
            """,
                recipient_data,
            )

        record_count += 1

    conn.commit()

    # インデックスとトリガーを作成
    print("インデックスとFTSを作成中...")
    cursor.executescript(SQL_CREATE_INDEXES_TRIGGERS)
    cursor.execute('INSERT INTO emails_fts(emails_fts) VALUES("rebuild")')
    conn.commit()

    print(f"データベース作成完了: {record_count} 通のメール")
    print(f"スキップ: {skipped_count} 通（長さ/受信者数制限）")
    print(f"重複スキップ: {duplicate_count} 通")
    return conn


def get_db_connection() -> sqlite3.Connection:
    """
    データベース接続を取得（シングルトン）
    
    既存のデータベースがあれば接続し、なければ新規作成します。
    
    Returns:
        sqlite3.Connection: データベース接続オブジェクト
    """
    global _db_conn
    if _db_conn is None:
        if os.path.exists(DB_PATH):
            print(f"既存のデータベースを読み込み中: {DB_PATH}")
            _db_conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        else:
            _db_conn = create_email_database()
    return _db_conn


# ===========================================
# メール検索・読み込み関数
# ===========================================

def search_emails(
    inbox: str,
    keywords: List[str],
    from_addr: Optional[str] = None,
    to_addr: Optional[str] = None,
    sent_after: Optional[str] = None,
    sent_before: Optional[str] = None,
    max_results: int = 10,
) -> List[SearchResult]:
    """
    キーワードとフィルタに基づいてメールを検索
    
    Args:
        inbox: 検索対象のメールボックス（メールアドレス）
        keywords: 検索キーワードのリスト
        from_addr: 送信者でフィルタ（オプション）
        to_addr: 受信者でフィルタ（オプション）
        sent_after: この日付以降のメール（オプション）
        sent_before: この日付以前のメール（オプション）
        max_results: 最大結果数（最大10）
    
    Returns:
        List[SearchResult]: 検索結果のリスト
    
    Raises:
        ValueError: キーワードが空または max_results > 10 の場合
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    where_clauses: List[str] = []
    params: List[str | int] = []

    if not keywords:
        raise ValueError("検索キーワードが指定されていません")

    if max_results > 10:
        raise ValueError("max_resultsは10以下である必要があります")

    # FTS5クエリ構築（デフォルトはAND検索）
    fts_query = " ".join(f""" "{k.replace('"', '""')}" """ for k in keywords)
    where_clauses.append("fts.emails_fts MATCH ?")
    params.append(fts_query)

    # メールボックスフィルタ（送信者または受信者として含まれるメール）
    where_clauses.append("""
        (e.from_address = ? OR EXISTS (
            SELECT 1 FROM recipients r_inbox
            WHERE r_inbox.recipient_address = ? AND r_inbox.email_id = e.message_id
        ))
    """)
    params.extend([inbox, inbox])

    # 送信者フィルタ
    if from_addr:
        where_clauses.append("e.from_address = ?")
        params.append(from_addr)

    # 受信者フィルタ
    if to_addr:
        where_clauses.append("""
            EXISTS (
                SELECT 1 FROM recipients r_to
                WHERE r_to.recipient_address = ? AND r_to.email_id = e.message_id
            )
        """)
        params.append(to_addr)

    # 日付範囲フィルタ
    if sent_after:
        where_clauses.append("e.date >= ?")
        params.append(f"{sent_after} 00:00:00")

    if sent_before:
        where_clauses.append("e.date < ?")
        params.append(f"{sent_before} 00:00:00")

    # SQLクエリ実行
    sql = f"""
        SELECT
            e.message_id,
            snippet(emails_fts, -1, '<b>', '</b>', ' ... ', 15) as snippet
        FROM
            emails e JOIN emails_fts fts ON e.id = fts.rowid
        WHERE
            {" AND ".join(where_clauses)}
        ORDER BY
            e.date DESC
        LIMIT ?;
    """
    params.append(max_results)

    cursor.execute(sql, params)
    results = cursor.fetchall()

    return [SearchResult(message_id=row[0], snippet=row[1]) for row in results]


def read_email(message_id: str) -> Optional[Email]:
    """
    メールIDから単一のメールを取得
    
    Args:
        message_id: 取得するメールのID
    
    Returns:
        Optional[Email]: メールオブジェクト（存在しない場合はNone）
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    # メール本体を取得
    cursor.execute(
        "SELECT message_id, date, subject, from_address, body, file_name FROM emails WHERE message_id = ?",
        (message_id,),
    )
    email_row = cursor.fetchone()

    if not email_row:
        return None

    msg_id, date, subject, from_addr, body, file_name = email_row

    # 受信者を取得
    cursor.execute(
        "SELECT recipient_address, recipient_type FROM recipients WHERE email_id = ?",
        (message_id,),
    )
    recipient_rows = cursor.fetchall()

    to_addresses = []
    cc_addresses = []
    bcc_addresses = []

    for addr, type_val in recipient_rows:
        if type_val.lower() == "to":
            to_addresses.append(addr)
        elif type_val.lower() == "cc":
            cc_addresses.append(addr)
        elif type_val.lower() == "bcc":
            bcc_addresses.append(addr)

    return Email(
        message_id=msg_id,
        date=date,
        subject=subject,
        from_address=from_addr,
        to_addresses=to_addresses,
        cc_addresses=cc_addresses,
        bcc_addresses=bcc_addresses,
        body=body,
        file_name=file_name,
    )


# ===========================================
# シナリオ読み込み関数
# ===========================================

def load_scenarios(
    split: Literal["train", "test"] = "train",
    limit: Optional[int] = None,
    max_messages: Optional[int] = 1,
    shuffle: bool = False,
    seed: Optional[int] = None,
) -> List[Scenario]:
    """
    Hugging Faceデータセットからシナリオを読み込み
    
    Args:
        split: データセット分割（"train" または "test"）
        limit: 読み込むシナリオ数の上限（オプション）
        max_messages: 参照メッセージ数の上限（オプション）
        shuffle: シャッフルするかどうか
        seed: 乱数シード（オプション）
    
    Returns:
        List[Scenario]: シナリオのリスト
    """
    print(f"{split}シナリオをHugging Faceから読み込み中...")
    dataset: Dataset = load_dataset(SCENARIO_DATASET_REPO_ID, split=split)

    # 参照メッセージ数でフィルタ
    if max_messages is not None:
        dataset = dataset.filter(lambda x: len(x["message_ids"]) <= max_messages)

    # シャッフル処理
    if shuffle or (seed is not None):
        if seed is not None:
            dataset = dataset.shuffle(seed=seed)
        else:
            dataset = dataset.shuffle()

    # Scenarioオブジェクトに変換
    scenarios = [Scenario(**row, split=split) for row in dataset]

    # 再度max_messagesでフィルタ（念のため）
    if max_messages is not None:
        scenarios = [s for s in scenarios if len(s.message_ids) <= max_messages]

    # Pythonレベルでもシャッフル
    if shuffle:
        if seed is not None:
            rng = random.Random(seed)
            rng.shuffle(scenarios)
        else:
            random.shuffle(scenarios)

    # 上限適用
    if limit is not None:
        scenarios = scenarios[:limit]

    print(f"{len(scenarios)} 件のシナリオを読み込みました")
    return scenarios


