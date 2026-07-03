#!/usr/bin/env python3
"""A-share LHB (Dragon Tiger List) fetch + LLM summary via OpenAI-compatible API."""

from __future__ import annotations

import argparse
import logging
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Callable

import akshare as ak
import httpx
import pandas as pd
import yaml
from openai import OpenAI

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

ROOT = Path(__file__).resolve().parent
DEFAULT_CONFIG = ROOT / "config.yaml"
SOURCE_GAP_SEC = 2.0


def ymd_compact(date_str: str) -> str:
    return date_str.replace("-", "")[:8]


def retry_call(fn: Callable[[], pd.DataFrame], *, retries: int = 3, delay: float = 2.5) -> pd.DataFrame:
    last_err: Exception | None = None
    for attempt in range(retries):
        try:
            return fn()
        except Exception as exc:
            last_err = exc
            if attempt < retries - 1:
                time.sleep(delay)
    assert last_err is not None
    raise last_err


def _normalize_em(df: pd.DataFrame, trade_date: str) -> pd.DataFrame:
    if df.empty:
        return df
    return pd.DataFrame(
        {
            "trade_date": [trade_date] * len(df),
            "symbol": df["代码"].astype(str).str.zfill(6),
            "name": df["名称"].astype(str),
            "reason": df.get("上榜原因", "").astype(str),
            "net_buy": pd.to_numeric(df.get("龙虎榜净买额"), errors="coerce").fillna(0),
            "buy_amount": pd.to_numeric(df.get("龙虎榜买入额"), errors="coerce").fillna(0),
            "sell_amount": pd.to_numeric(df.get("龙虎榜卖出额"), errors="coerce").fillna(0),
        }
    )


def _normalize_sina(df: pd.DataFrame, trade_date: str) -> pd.DataFrame:
    if df.empty:
        return df
    return pd.DataFrame(
        {
            "trade_date": [trade_date] * len(df),
            "symbol": df["股票代码"].astype(str).str.zfill(6),
            "name": df["股票名称"].astype(str),
            "reason": df.get("指标", "").astype(str),
            "net_buy": 0.0,
            "buy_amount": 0.0,
            "sell_amount": 0.0,
        }
    )


def fetch_lhb_daily(trade_date: str, *, retries: int = 3, delay: float = 2.5) -> tuple[pd.DataFrame, str]:
    compact = ymd_compact(trade_date)
    td = trade_date[:10]

    sources: list[tuple[str, Callable[[], pd.DataFrame], Callable[[pd.DataFrame, str], pd.DataFrame]]] = [
        ("em", lambda: ak.stock_lhb_detail_em(start_date=compact, end_date=compact), _normalize_em),
        ("sina", lambda: ak.stock_lhb_detail_daily_sina(date=compact), _normalize_sina),
    ]

    last_err: Exception | None = None
    saw_empty = False
    for i, (tag, fn, normalizer) in enumerate(sources):
        if i > 0:
            time.sleep(SOURCE_GAP_SEC)
        try:
            raw = retry_call(fn, retries=retries, delay=delay)
            df = normalizer(raw, td)
            if not df.empty:
                if tag != "em":
                    logger.info("LHB fallback source=%s date=%s rows=%d", tag, td, len(df))
                return df, tag
            saw_empty = True
        except Exception as exc:
            last_err = exc
            logger.warning("LHB source=%s date=%s failed: %s", tag, td, exc)

    if saw_empty:
        return pd.DataFrame(), "empty"
    assert last_err is not None
    raise last_err


def find_recent_lhb(max_days: int = 12) -> tuple[str, pd.DataFrame, str]:
    today = datetime.now().date()
    for offset in range(max_days):
        day = today - timedelta(days=offset)
        if day.weekday() >= 5:
            continue
        td = day.isoformat()
        try:
            df, source = fetch_lhb_daily(td)
        except Exception as exc:
            logger.debug("skip %s: %s", td, exc)
            continue
        if not df.empty:
            return td, df, source
    raise RuntimeError(f"No LHB data found in the last {max_days} calendar days")


def load_config(path: Path) -> dict:
    if not path.exists():
        raise FileNotFoundError(
            f"Config not found: {path}\nCopy config.example.yaml to config.yaml and set LLM_API_KEY."
        )
    with path.open(encoding="utf-8") as f:
        cfg = yaml.safe_load(f) or {}
    for key in ("LLM_BASE_URL", "LLM_MODEL", "LLM_API_KEY"):
        if not cfg.get(key) or cfg[key] == "your-key-here":
            raise ValueError(f"Set {key} in {path}")
    return cfg


def format_lhb_table(df: pd.DataFrame, top_n: int = 25) -> str:
    view = df.copy()
    if "net_buy" in view.columns:
        view = view.sort_values("net_buy", ascending=False)
    lines: list[str] = []
    for _, row in view.head(top_n).iterrows():
        net = row.get("net_buy", 0)
        net_txt = f" net={net:,.0f}" if net else ""
        lines.append(f"- {row['symbol']} {row['name']} | {row.get('reason', '')}{net_txt}")
    return "\n".join(lines)


def summarize_lhb(client: OpenAI, model: str, trade_date: str, table: str, lang: str) -> str:
    if lang == "zh":
        system = "你是 A 股量化研究员，用简洁中文总结龙虎榜要点，突出资金方向与板块线索。"
        user = (
            f"交易日 {trade_date} 龙虎榜（按净买额排序，单位元）：\n\n{table}\n\n"
            "请输出：1) 3 条核心观察 2) 2 个需跟踪的标的 3) 1 句风险提示（非投资建议）。"
        )
    else:
        system = "You are a China A-share quant analyst. Summarize LHB (dragon-tiger list) in concise English."
        user = (
            f"Trade date {trade_date}, China A-share LHB (sorted by net buy, CNY):\n\n{table}\n\n"
            "Output: 1) 3 key observations 2) 2 names to watch 3) one-line risk note (not investment advice)."
        )

    resp = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        temperature=0.4,
    )
    return (resp.choices[0].message.content or "").strip()


def main() -> int:
    parser = argparse.ArgumentParser(description="Fetch A-share LHB and summarize with an OpenAI-compatible LLM.")
    parser.add_argument("--date", help="Trade date YYYY-MM-DD (default: latest available)")
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG, help="Path to config.yaml")
    parser.add_argument("--top", type=int, default=25, help="Max rows sent to LLM")
    parser.add_argument("--lang", choices=("en", "zh"), default="en", help="Summary language")
    parser.add_argument("--model", help="Override LLM_MODEL from config")
    parser.add_argument("--no-llm", action="store_true", help="Only print LHB table, skip LLM call")
    args = parser.parse_args()

    if args.date:
        trade_date = args.date[:10]
        df, source = fetch_lhb_daily(trade_date)
        if df.empty:
            logger.error("No LHB data for %s", trade_date)
            return 1
    else:
        trade_date, df, source = find_recent_lhb()

    table = format_lhb_table(df, top_n=args.top)
    print(f"\n=== LHB {trade_date} (source={source}, rows={len(df)}) ===\n")
    print(table)
    print()

    if args.no_llm:
        return 0

    cfg = load_config(args.config)
    model = args.model or cfg["LLM_MODEL"]
    client = OpenAI(
        base_url=cfg["LLM_BASE_URL"],
        api_key=cfg["LLM_API_KEY"],
        default_headers={"User-Agent": "qinghong-open-traffic/1.0"},
        http_client=httpx.Client(timeout=120.0),
    )
    print(f"=== LLM summary ({model}) ===\n")
    summary = summarize_lhb(client, model, trade_date, table, args.lang)
    print(summary)
    print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
