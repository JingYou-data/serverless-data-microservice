# Customer Data Ingestion Script

🎯 **Mission**: Extract ~100,000 customer records from an unstable legacy CRM API and save to S3.

---

## Architecture Decision Record (ADR)

### Decision 1: Output Format - **CSV** 

**Chosen Format**: CSV (Comma-Separated Values)

**Reasoning**:
1. **Memory Efficiency**: Supports streaming writes - append records line-by-line without loading 100k records into RAM
2. **Recoverability**: If script crashes at page 50, we already have 49 pages written to disk
3. **Simplicity**: No complex batching logic required (unlike Parquet)
4. **Universal Compatibility**: Works with Excel, Pandas, SQL, and all data tools

**Trade-offs Considered**:
- **JSON**: Requires full structure in memory OR non-standard `.ndjson` format
- **Parquet**: Better compression but requires batching and more dependencies
- **CSV**: Winner for "extract first, optimize later" strategy

---

### Decision 2: Cleaning Strategy - **ELT (Extract-Load-Transform)** 

**Chosen Strategy**: Extract raw data first, clean later

**Reasoning**:
1. **Stability First**: Ingestion shouldn't fail due to data quality issues
2. **Flexibility**: Can adjust cleaning logic multiple times without re-extracting
3. **Auditability**: Preserve original "dirty" data for debugging
4. **Separation of Concerns**: Extraction and cleaning are independent processes

**Implementation**:
- Use `record.get('key', 'N/A')` for safe field access
- Track missing field statistics
- Write raw data "as-is" to S3
- Clean in subsequent SQL/Pandas step

**Trade-offs Considered**:
- **ETL (Clean-on-the-fly)**: Pro: Clean data immediately. Con: Risk losing data if cleaning fails
- **ELT (Extract-then-clean)**: Pro: Rarely fails. Con: S3 data needs post-processing ✅

---

##  System Architecture
```
┌─────────────────┐
│  Legacy CRM API │  (Unstable, rate-limited)
└────────┬────────┘
         │
         ├─ Exponential Backoff (1s, 2s, 4s, 8s...)
         ├─ Jitter (prevents thundering herd)
         ├─ Retry Logic (max 5 attempts)
         │
         ▼
┌─────────────────┐
│  Python Script  │
│   ingest.py     │
└────────┬────────┘
         │
         ├─ Streaming CSV Writer (append mode)
         ├─ Safe field access (.get())
         │
         ▼
┌─────────────────┐
│  Local CSV File │  (customers_extract_YYYYMMDD.csv)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   AWS S3 Bucket │
│  /raw/customers │
│  /date=YYYY-MM-DD
└─────────────────┘
```

---

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- AWS credentials configured (`~/.aws/credentials` or environment variables)
- API token from instructor

### Installation
```bash
# 1. Clone or download the project
cd customer-ingestion

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure environment
cp .env.example .env
nano .env  # Edit with your actual credentials
```

### Configuration

Edit `.env` file:
```bash
# Required
API_BASE_URL=https://your-api-url.com
API_TOKEN=your_actual_token_here
S3_BUCKET=your-bucket-name

# Optional (has defaults)
MAX_RETRIES=5
RECORDS_PER_PAGE=1000
```

### Run
```bash
python ingest.py
```

---

## 📊 Expected Output
```
🚀 开始数据提取...
📍 API: https://api.example.com/api/v1/customers
📦 S3 目标: s3://my-bucket/raw/customers/
--------------------------------------------------

📊 获取元数据...
✅ 总页数: 125
✅ 每页记录数: 1000
✅ 预计总记录数: ~125,000

✅ 第 1/125 页: 800 条记录
📥 第 2/125 页... ✅ 1000 条记录
📥 第 3/125 页... ⚠️  服务器错误 (500) - 重试 1/5，等待 1.2s...
📥 第 3/125 页... ✅ 1000 条记录
...

==================================================
--- Execution Report ---
==================================================
Pages Requested: 125
Successful Pages: 124
Failed Pages: 1
Total Retries: 14
Records Ingested: 99,400
Execution Time: 4m 12s
Format Chosen: CSV (Reason: Streaming efficiency)
==================================================
```

---

## 🔍 Features

### 1. Exponential Backoff with Jitter
```python
wait_time = 2^attempt + random_jitter
# Prevents "thundering herd" when entire class retries simultaneously
```

### 2. Streaming CSV Writer
```python
# NOT this (memory inefficient):
all_data = []
for page in pages:
    all_data.extend(fetch(page))  # ❌ 100k records in RAM
write_csv(all_data)

# THIS (streaming):
for page in pages:
    records = fetch(page)
    writer.write_records(records)  # ✅ Write immediately
```

### 3. Safe Field Access
```python
# NOT this:
email = record['email']  # ❌ Crashes if missing

# THIS:
email = record.get('email', 'N/A')  # ✅ Graceful fallback
```

### 4. Rate Limit Handling
- 429 errors trigger longer backoff (2x base wait)
- Different strategy than 500/503 errors

---

## 📁 Output Files

### Local
```
customers_extract_20251119_143022.csv
```

### S3
```
s3://your-bucket/raw/customers/date=2025-11-19/customers_extract_20251119_143022.csv
```

---

## 🧪 Testing

### Test with a small page limit first:
```python
# In config.py or .env
RECORDS_PER_PAGE=10  # Start small
```

### Simulate failures:
The API will naturally return 500/503/429 errors. Watch the retry logic in action!

---

## 🛠️ Troubleshooting

### Issue: "Missing API_TOKEN"
**Solution**: Check `.env` file exists and has correct values

### Issue: "403 Forbidden"
**Solution**: Token expired or incorrect. Get new token from instructor

### Issue: Script crashes on page 50
**Solution**: CSV file is saved! Contains first 49 pages. Script can be modified to resume.

### Issue: High memory usage
**Solution**: Already optimized! CSV streaming prevents loading all data in RAM.

---

## 📚 Key Learnings

1. ✅ **Production-grade error handling** (retries, timeouts, exceptions)
2. ✅ **Exponential backoff algorithm** (prevents thundering herd)
3. ✅ **Streaming processing** (handle big data without big RAM)
4. ✅ **State tracking** (success/failure/retry counts)
5. ✅ **Defensive programming** (safe field access, graceful degradation)

---

## 👥 Author

[Your Name]  
Data Engineering Project  
[Date]

---

## 📜 License

Educational project - use freely
```

---

## 🎯 额外文件：`.gitignore`

创建这个文件防止敏感信息被提交到 Git：
```
# 环境变量（敏感信息）
.env

# 数据文件
*.csv
*.json
*.parquet

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
.venv/

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db