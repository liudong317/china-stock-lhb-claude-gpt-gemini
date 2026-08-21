# A股龙虎榜演示 × OpenAI 兼容 LLM · 兼大 A 行情 API 说明

> **声明：** 本仓库演示与文档仅供个人学习、量化研究使用。数据与模型输出**不构成投资建议**，风险自担。

本仓两块内容：

1. **开源演示**：用 akshare 拉龙虎榜 + 晴红 LLM 中转（OpenAI 兼容）一键摘要  
2. **托管行情 API 说明**（表格）：报价 / 日K / 涨停情绪 / 资金 / 龙虎榜 / 基本面等 —— 与「资讯热榜 API」互补  

---

## 一、开源演示（本仓库代码）

| 步骤 | 说明 |
|------|------|
| 安装 | `pip install -r requirements.txt` |
| 配置 | `cp config.example.yaml config.yaml`，填 LLM Key |
| 运行 | `python analyze_lhb.py --lang zh` |
| 仅数据 | `python analyze_lhb.py --no-llm --lang zh` |

```yaml
LLM_BASE_URL: "https://www.qinghong.tech/v1"
LLM_MODEL: "glm-5.2"   # 也可 gpt / claude / gemini 等广场模型名
LLM_API_KEY: "your-key-here"
```

LLM 注册与文档：https://www.qinghong.tech/ · https://qinghongkeji.apifox.cn  

---

## 二、托管「大 A 行情 / 量化数据 API」能帮你做什么

> 资讯快讯请用：[finance-news-api-for-ai-agents](https://github.com/liudong317/finance-news-api-for-ai-agents)。  
> 行情飞书说明（对客主文档）：https://my.feishu.cn/wiki/WB5XwdSehi5Z3ikc6UfcgkyQnNd  

| 你能搭的场景 | 用到的能力 |
|--------------|------------|
| 盯盘看板 | 近时报价批量 + 大盘指数与成交额 |
| 复盘日报 | 涨停池 / 连板天梯 / 情绪 / 板块 / 龙虎榜 |
| 日K回测底稿 | 股票 / 主流 ETF / 可转债 `period=1d` |
| 查一只股票 | 报价 + 基本面估值 + 题材；Pro 再加财务 / 日线资金 |
| 本地智能体 | MCP / HTTP：「拉茅台报价」「今日涨停」 |

**和资讯的分工**：本 API = 行情 / K 线 / 资金情绪；资讯仓 = 热榜 / 快讯 / 正文。

---

## 三、行情 API · 接入与套餐（摘要）

| 项 | 说明 |
|----|------|
| 基址 | `https://api.qinghong888.cc.cd` |
| 鉴权 | Header `X-API-Key: 你的Key`（文档示例勿填真实 Key） |
| 健康检查 | `GET /health`（**不是** `/v1/health`） |
| 业务前缀 | `/v1/...` |
| 时区 | 北京时间交易日 |

| 档位 | 大致能力 | 说明 |
|------|----------|------|
| 日轮换试用 / 周测 | 同标准能力 | 便于联调 |
| 标准 | 报价、日K、涨停/情绪/板块、盘中资金、龙虎榜、基本面等 | 见下表 |
| Pro | 标准全部 + 日线资金 + 季频财务 + 证券资料 + 除权/复权 | 分钟K / Level-2 走发货网盘，不经本 API |

价格与配额以飞书为准。闲鱼店铺可搜「市场数据接口」；微信 **ziyouxiaoqi123**。

---

## 四、行情接口一览（表格）

### 公共

| 路径 | 作用 |
|------|------|
| `/health` | 探活 |
| `/v1/me` | 账户 / 配额 / 目录 |
| `/v1/markets/status` | 交易时段状态 |

### 大 A · 标准可用

| 路径 | 作用 | 能帮你 |
|------|------|--------|
| `/v1/cn/quote` | 近时报价 | 股票 / ETF / 可转债同一接口 |
| `/v1/cn/indices` | 大盘指数与成交额 | 含海外三大指数昨收参考字段 |
| `/v1/cn/kline?period=1d` | 日K | 回测底稿 |
| `/v1/cn/limit-up` | 涨停池 | 复盘 |
| `/v1/cn/limit-up-ladder` | 连板天梯 | 情绪结构 |
| `/v1/cn/hot-stocks` · `/skyrocket` · `/anomaly` | 热股 / 飙升 / 异动 | 题材追踪 |
| `/v1/cn/sentiment` | 市场情绪 | 日报 |
| `/v1/cn/sectors` | 板块 | 涨跌幅等 |
| `/v1/cn/moneyflow` | 盘中资金流 | 与 Pro 日线资金口径不同 |
| `/v1/cn/lhb` | 龙虎榜 | 与本仓 akshare 演示互补（托管版） |
| `/v1/cn/fundamentals` | 基本面估值 | 查一只股票 |
| `/v1/cn/industry` · `/concept` | 行业 / 题材概念 | 归类 |
| `/v1/cn/index-members` · `/macro` | 指数成分 / 宏观利率 | 扩展 |

### 大 A · Pro 另增

| 路径 | 作用 |
|------|------|
| `/v1/cn/dayfund` | 日线资金（收盘整理） |
| `/v1/cn/finance` | 季频财务 |
| `/v1/cn/stock-basic` | 证券资料 |
| `/v1/cn/dividend` · `/adjust-factor` | 除权除息 / 复权因子 |

### 国内期货（Key 已开通时）

| 路径 | 作用 |
|------|------|
| `/v1/cn-futures/quote` · `/kline` · `/list` | 报价 / 日K / 品种列表 |

```bash
export BASE=https://api.qinghong888.cc.cd
export KEY=你的Key

curl -sS "$BASE/health"
curl -sS -H "X-API-Key: $KEY" "$BASE/v1/me"
curl -sS -H "X-API-Key: $KEY" "$BASE/v1/cn/quote?symbols=600519,000001"
curl -sS -H "X-API-Key: $KEY" "$BASE/v1/cn/lhb?date=2026-08-20"
```

---

## 五、交流

若你在用本项目做 A 股量化、龙虎榜或行情 API 接入，欢迎加入个人量化交流群（免费，约 100 人）。

群内主要聊：数据接口、策略思路、部署踩坑、LLM 接入经验等。**仅供学习交流，不构成任何投资建议。**

另招代理，你不需要花费任何费用，各个平台可挂（如闲鱼，小红书，淘宝等平台），每天只需维护平台，养号就行，卖出去，前期3:7分，如果量大可再议价，联系客服👇，备注来意，无标明不回。

- 加微信：**ziyouxiaoqi123**（备注：**GitHub-LHB**）
- 群二维码：

![量化交流群二维码](./assets/wechat-group-qr.png)

**相关链接：**

| 链接 | 作用 |
|------|------|
| 行情飞书文档 | https://my.feishu.cn/wiki/WB5XwdSehi5Z3ikc6UfcgkyQnNd |
| 资讯 / 热榜 API 仓 | https://github.com/liudong317/finance-news-api-for-ai-agents |
| 资讯飞书 | https://my.feishu.cn/wiki/T7XWwCxtIiOcLIkkXQbc5I1Tntc |
| 状态页 | https://status.xiaobao317.site/ |
| LLM 中转 | https://www.qinghong.tech/ |

> 群内仅交流；API Key 请走闲鱼/淘宝正规渠道购买。**勿把 Key 提交到 Git。**

## 协议

MIT — 见 [LICENSE](LICENSE)。
