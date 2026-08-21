# China A-Share LHB Demo · Claude / GPT / Gemini + Market API notes

> For learning / quant research only — **not investment advice**.

**中文详细说明（推荐）→ [README.gitee.md](README.gitee.md)**

This repo includes:

1. **Open-source demo**: akshare Dragon Tiger List (LHB) + OpenAI-compatible LLM summary  
2. **Hosted A-share market API overview** (tables): quotes, daily bars, limit-up, moneyflow, LHB, fundamentals — complementary to the [finance news API](https://github.com/liudong317/finance-news-api-for-ai-agents)

---

## Quick start (demo)

```bash
pip install -r requirements.txt
cp config.example.yaml config.yaml
python analyze_lhb.py
```

```yaml
LLM_BASE_URL: "https://www.qinghong.tech/v1"
LLM_MODEL: "gpt-5.5"
LLM_API_KEY: "your-key-here"
```

---

## Hosted market API · what it helps with

| Use case | Endpoints (examples) |
|----------|----------------------|
| Watchlist quotes | `GET /v1/cn/quote` |
| Index & turnover | `GET /v1/cn/indices` |
| Daily bars / backtest | `GET /v1/cn/kline?period=1d` |
| Limit-up / sentiment / sectors | `/v1/cn/limit-up`, `/sentiment`, `/sectors` |
| Intraday moneyflow | `GET /v1/cn/moneyflow` |
| Dragon Tiger List | `GET /v1/cn/lhb` |
| Fundamentals / concepts | `/v1/cn/fundamentals`, `/concept` |
| Pro: dayfund / finance | `/v1/cn/dayfund`, `/finance`, … |

| | |
|--|--|
| Base | `https://api.qinghong888.cc.cd` |
| Auth | `X-API-Key: YOUR_KEY` (never commit real keys) |
| Docs | https://my.feishu.cn/wiki/WB5XwdSehi5Z3ikc6UfcgkyQnNd |

News / hot ranks → https://github.com/liudong317/finance-news-api-for-ai-agents  

---

## Community / 交流

If you use this repo for **A-share quant**, **LHB**, or **market API** integration — welcome to our free WeChat group (~100).

群内主要交流：数据接口用法、策略思路、部署踩坑、LLM 接入经验等。**仅供学习交流，不构成任何投资建议。**

另招代理，你不需要花费任何费用，各个平台可挂（如闲鱼，小红书，淘宝等平台），每天只需维护平台，养号就行，卖出去，前期3:7分，如果量大可再议价，联系客服👇，备注来意，无标明不回。

- WeChat / 微信：**ziyouxiaoqi123**（备注 / note：**GitHub-LHB**）
- 或扫下方群二维码：

![量化交流群二维码](./assets/wechat-group-qr.png)

> 群内仅交流；API Key 请走闲鱼/淘宝正规渠道购买。

## License

MIT — see [LICENSE](LICENSE).
