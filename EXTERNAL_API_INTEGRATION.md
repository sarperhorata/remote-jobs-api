# 🌐 External API Integration - Buzz2Remote

Bu doküman, Buzz2Remote projesi için external job API entegrasyonunu açıklar.

## 📋 **MEVCUT ENTEGRASYONLAR**

### 🎯 **1. Fantastic Jobs API**
- **Provider**: [RapidAPI - Fantastic Jobs](https://rapidapi.com/fantastic-jobs-fantastic-jobs-default/api/active-jobs-db/)
- **Rate Limit**: 15 requests/month (max 500 jobs)
- **Schedule**: Her 2 günde bir (1,3,5,7,9,11,13,15,17,19,21,23,25,27,29)
- **Status**: ✅ Entegre edildi

### 🎯 **2. Job Posting Feed API**
- **Provider**: [RapidAPI - Job Posting Feed](https://rapidapi.com/fantastic-jobs-fantastic-jobs-default/api/job-posting-feed-api/)
- **Rate Limit**: 5 requests/month (max 500 jobs per request)
- **Schedule**: Haftada bir (1,8,15,22,29)
- **Status**: ✅ Entegre edildi

### 🎯 **3. RemoteOK API**
- **Provider**: [RapidAPI - Jobs from RemoteOK](https://rapidapi.com/Flatroy/api/jobs-from-remoteok/)
- **Rate Limit**: 24 requests/day
- **Schedule**: Günlük (her gün)
- **Status**: ✅ Entegre edildi

### 🎯 **4. Arbeitnow Free Job Board API**
- **Provider**: [RapidAPI - Arbeitnow Free Job Board](https://rapidapi.com/arbeitnow/api/arbeitnow-free-job-board/)
- **Rate Limit**: 500,000 requests/month, 1000/hour 🎉
- **Schedule**: Günlük (her gün) - çok cömert rate limit
- **Status**: ✅ Entegre edildi

## 🛠️ **SİSTEM YAPISI**

### **Core Files**
```
external_job_apis.py       # Ana entegrasyon modülü
cron_external_apis.py      # Cronjob scheduler
setup_external_api_cron.sh # Crontab kurulum scripti
```

### **Data Structures**
```python
@dataclass
class JobData:
    title: str
    company: str 
    location: str
    description: str
    url: str
    salary: Optional[str]
    job_type: Optional[str]
    posted_date: Optional[str]
    source: str
    external_id: str

@dataclass
class CompanyData:
    name: str
    description: Optional[str]
    website: Optional[str]
    industry: Optional[str]
    size: Optional[str]
    location: Optional[str]
```

## ⚙️ **KURULUM**

### **1. Environment Variables**
```bash
export TELEGRAM_BOT_TOKEN='your_bot_token'
export TELEGRAM_CHAT_ID='your_chat_id' 
export RAPIDAPI_KEY='your_rapidapi_key'  # Optional, hardcoded for now
```

### **2. Crontab Setup**
```bash
# Otomatik kurulum
chmod +x setup_external_api_cron.sh
./setup_external_api_cron.sh

# Manuel kurulum
crontab -e
# Add: 0 9 * * * cd /path/to/buzz2remote && python3 cron_external_apis.py >> external_api_cron.log 2>&1
```

### **3. Dependencies**
```bash
pip install requests python-dateutil
```

## 📊 **RATE LIMITING SYSTEM**

### **Rate Limit Strategy**
- **Fantastic Jobs**: 15 requests/month = her 2 günde 1 crawl
- **Job Posting Feed**: 5 requests/month = haftada 1 crawl (ultra konservatif)
- **RemoteOK**: 24 requests/day = günlük crawl
- **Arbeitnow Free**: 500,000 requests/month = günlük crawl (süper cömert! 🎉)
- **Smart Scheduling**: Fantastic (1,3,5,7,9,11,13,15,17,19,21,23,25,27,29), Job Posting (1,8,15,22,29), RemoteOK & Arbeitnow (her gün)
- **File-based Tracking**: `.api_requests_15_30.json`, `.api_requests_5_30.json`, `.api_requests_24_1.json`, `.api_requests_500000_30.json`

### **Rate Limit Kontrol**
```python
from external_job_apis import FantasticJobsAPI, JobPostingFeedAPI, RemoteOKAPI, ArbeitnowFreeAPI

fantastic_api = FantasticJobsAPI()
job_posting_api = JobPostingFeedAPI()
remoteok_api = RemoteOKAPI()
arbeitnow_api = ArbeitnowFreeAPI()

print(f"Fantastic Jobs: {fantastic_api.rate_limiter.requests_remaining()}/15")
print(f"Job Posting Feed: {job_posting_api.rate_limiter.requests_remaining()}/5")
print(f"RemoteOK: {remoteok_api.rate_limiter.requests_remaining()}/24")
print(f"Arbeitnow Free: {arbeitnow_api.rate_limiter.requests_remaining()}/500000")
```

## 🚀 **KULLANIM**

### **1. Manual Run**
```bash
# Tek API test
python3 external_job_apis.py

# Cronjob test  
python3 cron_external_apis.py

# Rate limit check
cat .api_requests_15_30.json
```

### **2. Programmatic Usage**
```python
from external_job_apis import ExternalJobAPIManager

manager = ExternalJobAPIManager()
jobs_data = manager.fetch_all_jobs(max_jobs_per_api=100)  # Job Posting Feed otomatik 500 limit
results = manager.save_jobs_to_database(jobs_data)
```

### **3. Add New API**
```python
class NewJobAPI:
    def __init__(self):
        self.rate_limiter = RateLimiter(max_requests=20, time_period_days=30)
        self.notifier = ServiceNotifier()
    
    def fetch_remote_jobs(self, limit: int = 100) -> List[JobData]:
        # Implementation here
        pass

# Add to manager
manager = ExternalJobAPIManager()
manager.apis['new_api'] = NewJobAPI()
```

## 📱 **TELEGRAM NOTIFICATIONS**

### **Notification Types**
- ✅ **Rate Limit Exceeded**: `⚠️ FANTASTIC JOBS API - RATE LIMIT`, `⚠️ JOB POSTING FEED API - RATE LIMIT`, `⚠️ REMOTEOK API - RATE LIMIT`
- ✅ **API Success**: `✅ FANTASTIC JOBS API - SUCCESS`, `✅ JOB POSTING FEED API - SUCCESS`, `✅ REMOTEOK API - SUCCESS`
- ❌ **API Error**: `❌ FANTASTIC JOBS API - ERROR`, `❌ JOB POSTING FEED API - ERROR`, `❌ REMOTEOK API - ERROR`
- 🔄 **Crawl Start**: `🚀 EXTERNAL APIS - STARTING CRAWL`
- ✅ **Crawl Complete**: `✅ EXTERNAL APIS - CRAWL COMPLETE`
- ⏳ **Scheduled Skip**: `⏳ EXTERNAL APIS - SCHEDULED SKIP`

### **Sample Notification**
```
✅ EXTERNAL APIS - CRAWL COMPLETE

🎉 Crawl başarıyla tamamlandı
📊 Toplam job: 125

🔧 API Sonuçları:
• Fantastic Jobs: 33 jobs
• Job Posting Feed: 45 jobs
• RemoteOK: 47 jobs

⏭️ Sonraki çalıştırma: 2025-05-26 09:00
🕐 Bitiş zamanı: 2025-05-25 20:45:27
```

## 📈 **MONITORING**

### **Health Checks**
```python
# Monitor services include edildi
from monitor_services import ServiceMonitor

monitor = ServiceMonitor()
# External API monitoring otomatik dahil
```

### **Log Files**
```bash
# Cron logs
tail -f external_api_cron.log

# Rate limit history
cat .api_requests_15_30.json  # Fantastic Jobs
cat .api_requests_5_30.json   # Job Posting Feed
cat .api_requests_24_1.json   # RemoteOK

# Job data
ls -la external_jobs_*.json
```

### **Metrics**
- **Rate Limit Usage**: 15/month (Fantastic), 5/month (Job Posting), 24/day (RemoteOK) tracking
- **Job Success Rate**: Jobs fetched vs errors
- **API Response Times**: Monitored automatically
- **Data Quality**: Job validation and deduplication
- **Remote Filtering**: Automatic remote job detection

## 🔧 **TROUBLESHOOTING**

### **Common Issues**

#### ❌ **"Rate limit exceeded"**
```bash
# Check current usage
cat .api_requests_15_30.json  # Fantastic Jobs
cat .api_requests_5_30.json   # Job Posting Feed
cat .api_requests_24_1.json   # RemoteOK

# Reset if needed (emergency only)
rm .api_requests_15_30.json
rm .api_requests_5_30.json
rm .api_requests_24_1.json
```

#### ❌ **"This endpoint is disabled for your subscription"**
```bash
# Check RapidAPI subscription status
# Update API endpoints in external_job_apis.py
# Test with different endpoints
```

#### ❌ **Cron job not running**
```bash
# Check crontab
crontab -l

# Check environment in cron
env | grep TELEGRAM

# Test manual run
python3 cron_external_apis.py
```

### **Debug Commands**
```bash
# Full debug run
TELEGRAM_CHAT_ID=-1002424698891 python3 -c "
from external_job_apis import FantasticJobsAPI, JobPostingFeedAPI, RemoteOKAPI

# Test all APIs
fantastic = FantasticJobsAPI()
job_posting = JobPostingFeedAPI()
remoteok = RemoteOKAPI()

print('Rate limits:')
print(f'Fantastic: {fantastic.rate_limiter.requests_remaining()}/15')
print(f'Job Posting: {job_posting.rate_limiter.requests_remaining()}/5')
print(f'RemoteOK: {remoteok.rate_limiter.requests_remaining()}/24')

# Test manager
from external_job_apis import ExternalJobAPIManager
manager = ExternalJobAPIManager()
results = manager.fetch_all_jobs(max_jobs_per_api=50)
for api, jobs in results.items():
    print(f'{api}: {len(jobs)} jobs')
"
```

## 📋 **NEXT STEPS**

### **Planned Integrations**
1. **Indeed API** - Job aggregation
2. **LinkedIn Jobs API** - Professional network
3. **AngelList API** - Startup jobs  
4. **Stack Overflow Jobs** - Developer focused
5. **Remote.co API** - Remote-first jobs

### **Feature Roadmap**
- [ ] Database integration (MongoDB)
- [ ] Job deduplication algorithm
- [ ] Company mapping and enrichment
- [ ] Advanced filtering and categorization
- [ ] API health monitoring dashboard
- [ ] Automatic retry on failures
- [ ] Performance analytics

## 🎯 **PERFORMANCE METRICS**

### **Current Status**
- **APIs Integrated**: 4 (Fantastic Jobs, Job Posting Feed, RemoteOK, Arbeitnow Free)
- **Rate Limit Efficiency**: Optimal scheduling for all APIs
- **Error Handling**: ✅ Comprehensive with notifications
- **Monitoring**: ✅ Real-time Telegram alerts
- **Scheduling**: ✅ Intelligent cron scheduling with per-API control
- **Remote Filtering**: ✅ Automatic remote job detection

### **Success Criteria**
- ✅ Rate limits respected (15/month + 5/month + 24/day + 500,000/month)
- ✅ Zero manual intervention required
- ✅ Real-time error notifications
- ✅ Structured data output
- ✅ Scalable architecture for new APIs
- ✅ Smart scheduling per API rate limits
- ✅ Daily RemoteOK crawling for fresh jobs

---

## 🔗 **USEFUL LINKS**

- [Fantastic Jobs RapidAPI](https://rapidapi.com/fantastic-jobs-fantastic-jobs-default/api/active-jobs-db/)
- [Buzz2Remote Main Project](../README.md)
- [Service Notifications](service_notifications.py)
- [Monitoring System](monitor_services.py)

---

**Last Updated**: 2025-05-25  
**Status**: ✅ Production Ready  
**Maintainer**: Buzz2Remote Team 