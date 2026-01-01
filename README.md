<div align="center">

# 🚀 CronWatch

### Never Miss a Scheduled Workflow Again

**The intelligent monitoring solution for GitHub Actions cron jobs**

[![GitHub Marketplace](https://img.shields.io/badge/Marketplace-CronWatch-blue.svg?colorA=24292e&colorB=0366d6&style=flat&longCache=true&logo=github)](https://github.com/marketplace)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)

[**Install Now**](https://github.com/apps/cronwatch) • [**Documentation**](#-quick-start) • [**Features**](#-features) • [**Pricing**](#-pricing)

</div>

---

## 🎯 Why CronWatch?

GitHub Actions scheduled workflows are critical for CI/CD, but they fail silently. **CronWatch ensures your cron jobs run on time, every time.**

### The Problem
- ⚠️ **Silent Failures**: Cron workflows fail without notifications
- 📉 **No Visibility**: Can't track success rates or runtime trends
- 🔍 **Hard to Debug**: No centralized view of all scheduled jobs
- ⏰ **Missed Runs**: No alerts when workflows don't execute on schedule

# ActionWatch

**Monitor your GitHub Actions cron workflows in one place.**

ActionWatch gives you a unified dashboard to track the health, status, and execution history of all your scheduled GitHub Actions. Never miss a silent failure again. Get instant notifications via Slack or Microsoft Teams when:
- **Missed Runs**: Workflow didn't execute when scheduled
- **Delayed Runs**: Workflow started later than expected
- **Stuck Workflows**: Long-running jobs that may be hanging
- **Anomalies**: Runtime significantly different from baseline

### 📊 **Analytics Dashboard**
Gain deep insights into your workflow health:
- **Success Rate Trends**: Track reliability over time
- **Runtime Analysis**: Identify performance degradation
- **Duration Statistics**: P50, P90, P95, P99 percentiles
- **Historical Data**: 30-day trend visualization

### 🎨 **Beautiful UI**
Modern, dark-themed interface with:
- **Organization Switcher**: Manage multiple GitHub orgs
- **Real-time Status**: Live workflow monitoring
- **Search & Filter**: Find workflows instantly
- **Keyboard Shortcuts**: Power-user navigation (`Cmd+K`, `Cmd+S`, etc.)

### 🔐 **Enterprise-Ready**
- **Multi-tenancy**: Separate data per organization
- **GitHub App Auth**: Secure, scoped permissions
- **Stripe Billing**: Professional subscription management
- **Feature Gating**: Free and Pro tiers

### 🚨 **Alert History**
- **Full Audit Trail**: Every alert logged and searchable
- **Acknowledgment**: Mark alerts as reviewed
- **Filtering**: By type, status, and time range
- **Export**: Download alert history (Pro)

---

## 🚀 Quick Start

### 1. Install the GitHub App

Click the button below to install CronWatch on your repositories:

[![Install CronWatch](https://img.shields.io/badge/Install-CronWatch-success?style=for-the-badge&logo=github)](https://github.com/apps/cronwatch)

### 2. Configure Alerts

1. Log in to [CronWatch Dashboard](https://cronwatch.app)
2. Select your organization
3. Click **Settings** (or press `Cmd+S`)
4. Add your Slack or Teams webhook URL
5. Configure alert thresholds

### 3. Start Monitoring

That's it! CronWatch automatically discovers all your scheduled workflows and starts monitoring them immediately.

---

## 📸 Screenshots

<div align="center">

### Dashboard Overview
![Dashboard](docs/images/dashboard.png)
*Monitor all your workflows at a glance with real-time status updates*

### Analytics Insights
![Analytics](docs/images/analytics.png)
*Track success rates, runtime trends, and performance metrics*

### Alert History
![Alerts](docs/images/alerts.png)
*Full audit trail of all triggered alerts with acknowledgment*

### Settings Panel
![Settings](docs/images/settings.png)
*Configure webhooks and alert thresholds per organization*

</div>

---

## 💡 Use Cases

### **DevOps Teams**
Monitor nightly builds, scheduled deployments, and automated testing across all repositories.

### **Data Engineering**
Track ETL pipelines, data sync jobs, and scheduled data processing workflows.

### **Security Teams**
Ensure security scans, compliance checks, and vulnerability assessments run on schedule.

### **Open Source Maintainers**
Monitor release automation, dependency updates, and scheduled maintenance tasks.

---

## 🎹 Keyboard Shortcuts

CronWatch is built for power users:

| Shortcut | Action |
|----------|--------|
| `Cmd/Ctrl + K` | Focus search |
| `Cmd/Ctrl + S` | Open settings |
| `Cmd/Ctrl + B` | Open billing |
| `Cmd/Ctrl + 1/2/3` | Switch views |
| `?` | Show all shortcuts |

---

## 💰 Pricing

<table>
<tr>
<td width="50%" valign="top">

### 🆓 **Free**
Perfect for individuals and small teams

- ✅ Unlimited workflows
- ✅ Unlimited repositories
- ✅ Basic alerts (Missed runs)
- ✅ Slack & Teams integration
- ✅ 7-day alert history
- ❌ Analytics dashboard
- ❌ Advanced alerts
- ❌ Alert history export

**$0/month**

</td>
<td width="50%" valign="top">

### ⭐ **Pro**
For teams that need deep insights

- ✅ **Everything in Free**
- ✅ **Analytics Dashboard**
- ✅ **Advanced Alerts**
  - Delayed runs
  - Stuck workflows
  - Runtime anomalies
- ✅ **Unlimited Alert History**
- ✅ **CSV Export**
- ✅ **Priority Support**

**$15/org/month**

[**Upgrade Now**](https://cronwatch.app/billing)

</td>
</tr>
</table>

---

## 🛠️ Self-Hosting

Want to run CronWatch on your own infrastructure? We've got you covered!

### Prerequisites
- Python 3.10+
- PostgreSQL 13+
- Node.js 18+
- GitHub App credentials
- (Optional) Stripe account for billing

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/cronwatch.git
cd cronwatch

# Backend setup
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Database setup
createdb gha_cron_monitor
python -m app.scripts.init_db

# Frontend setup
cd frontend
npm install
npm run build

# Configure environment
cp .env.example .env
# Edit .env with your credentials

# Run the application
# Backend
uvicorn app.main:app --reload

# Frontend (development)
cd frontend && npm run dev
```

### Environment Variables

```bash
# GitHub App
GITHUB_APP_ID=your_app_id
GITHUB_APP_PRIVATE_KEY_PATH=/path/to/private-key.pem
GITHUB_WEBHOOK_SECRET=your_webhook_secret
GITHUB_CLIENT_ID=your_oauth_client_id
GITHUB_CLIENT_SECRET=your_oauth_client_secret

# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/gha_cron_monitor

# Stripe (optional)
STRIPE_SECRET_KEY=sk_test_...
STRIPE_PUBLISHABLE_KEY=pk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...
STRIPE_PRICE_ID=price_...

# Frontend
FRONTEND_URL=http://localhost:5173
```

### Creating a GitHub App

1. Go to **Settings** → **Developer settings** → **GitHub Apps** → **New GitHub App**
2. Set the following permissions:
   - **Repository permissions**:
     - Actions: Read-only
     - Contents: Read-only
     - Metadata: Read-only
   - **Organization permissions**:
     - Members: Read-only
3. Subscribe to events:
   - Workflow run
   - Installation
   - Installation repositories
4. Generate a private key and save it
5. Install the app on your organization

---

## 🏗️ Architecture

```
┌─────────────────┐
│  GitHub Actions │
│   (Webhooks)    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐      ┌──────────────┐
│   FastAPI       │◄────►│  PostgreSQL  │
│   Backend       │      │   Database   │
└────────┬────────┘      └──────────────┘
         │
         ▼
┌─────────────────┐      ┌──────────────┐
│   React         │      │   Stripe     │
│   Frontend      │◄────►│   Billing    │
└─────────────────┘      └──────────────┘
         │
         ▼
┌─────────────────┐
│  Slack/Teams    │
│   Webhooks      │
└─────────────────┘
```

**Tech Stack:**
- **Backend**: FastAPI, SQLAlchemy, APScheduler
- **Frontend**: React, TypeScript, TailwindCSS, Recharts
- **Database**: PostgreSQL
- **Auth**: GitHub App OAuth
- **Billing**: Stripe
- **Deployment**: Docker, Kubernetes-ready

---

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Development Setup

```bash
# Install development dependencies
pip install -r requirements-dev.txt
cd frontend && npm install

# Run tests
pytest
npm test

# Format code
black app/
prettier --write frontend/src/
```

---

## 📚 Documentation

- [**API Reference**](docs/API.md) - Complete API documentation
- [**Webhook Guide**](docs/WEBHOOKS.md) - Setting up Slack/Teams webhooks
- [**Alert Types**](docs/ALERTS.md) - Understanding different alert types
- [**Troubleshooting**](docs/TROUBLESHOOTING.md) - Common issues and solutions

---

## 🔒 Security

- **Secure by Design**: Minimal GitHub permissions (read-only)
- **Data Privacy**: Your workflow data never leaves your infrastructure (self-hosted)
- **Encrypted**: All data encrypted in transit and at rest
- **Compliance**: SOC 2 Type II certified (coming soon)

Found a security issue? Please email security@cronwatch.app

---

## 📄 License

CronWatch is licensed under the [MIT License](LICENSE).

---

## 💬 Support

- 📧 **Email**: support@cronwatch.app
- 💬 **Discord**: [Join our community](https://discord.gg/cronwatch)
- 🐛 **Issues**: [GitHub Issues](https://github.com/yourusername/cronwatch/issues)
- 📖 **Docs**: [Documentation](https://docs.cronwatch.app)

---

## 🌟 Star History

[![Star History Chart](https://api.star-history.com/svg?repos=yourusername/cronwatch&type=Date)](https://star-history.com/#yourusername/cronwatch&Date)

---

<div align="center">

**Made with ❤️ by developers, for developers**

[Install CronWatch](https://github.com/apps/cronwatch) • [View Demo](https://demo.cronwatch.app) • [Read Docs](https://docs.cronwatch.app)

</div>
