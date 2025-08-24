# KRNL Multi-Agent Employee Onboarding System

A sophisticated **multi-agent system** that automates employee onboarding workflows using modern architecture patterns including **MCP (Multi-Cloud Protocol)** and **A2A (Agent-to-Agent)** communication.

## 🎯 Project Overview

This system demonstrates advanced concepts in distributed agent architectures by implementing a complete employee onboarding workflow with the following key features:

- **Multi-Agent Architecture**: 4 specialized agents working in coordination
- **MCP Compliance**: Standardized agent manifests and communication protocols
- **A2A Communication**: Direct agent-to-agent messaging capabilities
- **Full Traceability**: Comprehensive audit trails for all operations
- **Modern Web Dashboard**: Real-time monitoring and management interface
- **Containerized Deployment**: Docker-based microservices architecture

## 🏗️ System Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Frontend      │    │   API Gateway    │    │   Orchestrator  │
│  (Dashboard)    │◄──►│   (FastAPI)      │◄──►│   (Workflow)    │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │                        │
                                ▼                        ▼
┌─────────────────────────────────────────────────────────────────┐
│                     Agent Communication Bus                      │
│                        (Redis + A2A)                           │
└─────────────────────────────────────────────────────────────────┘
                                │
                ┌───────────────┼───────────────┐
                ▼               ▼               ▼               ▼
        ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
        │  Validator   │ │ Account Setup│ │  Scheduler   │ │  Notifier    │
        │    Agent     │ │    Agent     │ │    Agent     │ │    Agent     │
        └──────────────┘ └──────────────┘ └──────────────┘ └──────────────┘
                                │
                                ▼
                    ┌──────────────────────┐
                    │    PostgreSQL DB     │
                    │  (Audit & Storage)   │
                    └──────────────────────┘
```

## 🤖 Agent Architecture

### Agent A: Validator Agent
**Responsibility**: Data validation and cleaning
- Validates employee data completeness and format
- Performs data normalization and standardization  
- Provides detailed error reporting and warnings
- Handles multiple date formats and fuzzy string matching

### Agent B: Account Setup Agent
**Responsibility**: System account creation and permissions
- Generates unique usernames and system accounts
- Assigns role-based permissions based on job function
- Demonstrates **A2A communication** by directly calling Scheduler Agent
- Manages account lifecycle and status

### Agent C: Scheduler Agent 
**Responsibility**: Calendar event scheduling
- Creates comprehensive onboarding calendar schedules
- Integrates with Google Calendar API (mocked for demo)
- Includes **MCP manifest** defining capabilities and interfaces
- Handles multiple event types (orientation, HR meetings, team introductions)

### Agent D: Notifier Agent
**Responsibility**: Multi-channel notifications
- Sends email notifications to HR, managers, and employees
- Integrates with Slack for team notifications (mocked)
- Provides notification templates and personalization
- Tracks delivery status and maintains communication audit trails

## 🚀 Quick Start

### Prerequisites
- Docker and Docker Compose
- Git
- 8GB+ RAM recommended
- Ports 3000, 8000, 5432, 6379 available

### Installation & Setup

1. **Clone the repository**
```bash
git clone <repository-url>
cd krnl-onboarding-system
```

2. **Start the system**
```bash
docker-compose up -d
```

3. **Initialize the database**
```bash
# Database tables are auto-created on first run
# Check logs: docker-compose logs backend
```

4. **Access the dashboard**
```
Frontend Dashboard: http://localhost:3000
API Documentation: http://localhost:8000/docs
Health Check: http://localhost:8000/health
```

### Development Mode

For development with hot reload:

```bash
# Backend development
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000

# Frontend development  
cd frontend
# Serve with any HTTP server, e.g.:
python -m http.server 3000
```

## 📊 Dashboard Features

### Main Dashboard
- **Real-time Statistics**: Employee counts, success rates, system health
- **Recent Activity Feed**: Live workflow progress updates
- **System Status Monitor**: Agent performance and health indicators

### Employee Management
- **Individual Employee Creation**: Form-based employee data entry
- **Bulk CSV Upload**: Support for batch employee onboarding
- **Status Tracking**: Visual workflow progress indicators
- **Detailed Views**: Complete onboarding history and audit trails

### Workflow Monitoring
- **Real-time Progress**: Live updates of multi-agent workflows
- **Step-by-step Tracking**: Detailed progress through each agent
- **Performance Metrics**: Execution times and success rates
- **Error Diagnostics**: Comprehensive error reporting and resolution

### Audit & Logging
- **Agent Performance Analytics**: Success rates, execution times, error patterns
- **Log Search & Filtering**: Advanced search across all system logs
- **Traceability Reports**: Complete audit trails for compliance
- **System Health Monitoring**: Real-time system status and alerts

## 🔧 API Documentation

### Core Endpoints

#### Employee Management
```bash
# Create single employee
POST /api/v1/employees
Content-Type: application/json
{
  "name": "John Doe",
  "email": "john.doe@company.com", 
  "role": "Software Engineer",
  "department": "Engineering",
  "start_date": "2024-01-15"
}

# Bulk employee upload
POST /api/v1/employees/upload-csv
Content-Type: multipart/form-data
file: employees.csv

# List employees with status
GET /api/v1/employees?skip=0&limit=100

# Get employee details and full trace
GET /api/v1/employees/{employee_id}
```

#### Workflow Monitoring
```bash
# Get workflow status
GET /api/v1/workflows/{workflow_id}

# Get detailed workflow trace
GET /api/v1/workflows/{workflow_id}/trace
```

#### Dashboard & Analytics
```bash
# Dashboard statistics
GET /api/v1/dashboard/stats

# Recent activity
GET /api/v1/dashboard/recent-activity

# Agent performance metrics
GET /api/v1/audit/agent-performance/{agent_type}?days=7

# System health report
GET /api/v1/audit/system-health

# Search audit logs
POST /api/v1/audit/search-logs
{
  "agent_type": "validator",
  "status": "success",
  "start_date": "2024-01-01",
  "end_date": "2024-01-31"
}
```

## 🔄 Workflow Process

The complete onboarding workflow follows this sequence:

1. **Data Input** → Employee data received via API or CSV upload
2. **Validation** → Validator Agent cleans and validates all data
3. **Account Setup** → Account Setup Agent creates system accounts
4. **A2A Communication** → Account Agent directly notifies Scheduler Agent
5. **Event Scheduling** → Scheduler Agent creates calendar events
6. **Notifications** → Notifier Agent sends multi-channel notifications
7. **Completion** → Workflow marked complete with full audit trail

### MCP Implementation

The **Scheduler Agent** includes a complete MCP manifest (`/backend/agents/mcp_manifests/scheduler_agent_manifest.json`) demonstrating:

- **Standardized Interface Definitions**: Input/output schemas
- **Capability Declarations**: Supported operations and constraints
- **Communication Protocols**: HTTP, message queue, and A2A endpoints
- **Health Monitoring**: Status endpoints and metrics
- **Dependency Management**: External service requirements
- **Configuration Management**: Environment variables and settings

### A2A Communication Example

The system demonstrates **Agent-to-Agent** communication when the Account Setup Agent directly notifies the Scheduler Agent:

```python
# In Account Setup Agent
scheduler_response = await self.call_agent(
    target_agent="scheduler",
    method="account_created_notification", 
    params={
        "employee_id": str(employee_id),
        "employee_data": employee_data,
        "account_data": account_data
    }
)
```

This bypasses the central orchestrator and demonstrates direct agent communication patterns.

## 🧪 Testing

### Running Unit Tests
```bash
cd backend
python -m pytest tests/ -v

# Run specific test file
python -m pytest tests/test_validator_agent.py -v

# Run with coverage
python -m pytest tests/ --cov=agents --cov-report=html
```

### Test Coverage
The test suite includes comprehensive coverage for the Validator Agent:
- Input validation scenarios
- Data cleaning and normalization
- Error handling and edge cases  
- Date parsing and format handling
- Email validation and string similarity

## 🐳 Docker Services

The system runs as multiple containerized services:

### Core Services
- **Backend API** (`backend:8000`): FastAPI application with REST endpoints
- **Frontend** (`frontend:3000`): Nginx serving HTML/CSS/JavaScript dashboard
- **PostgreSQL** (`postgres:5432`): Primary database for all data storage
- **Redis** (`redis:6379`): Message queue and caching for A2A communication

### Agent Services
- **Validator Agent**: Data validation and cleaning service
- **Account Setup Agent**: System account creation service  
- **Scheduler Agent**: Calendar and event scheduling service
- **Notifier Agent**: Multi-channel notification service

### Service Health Monitoring
```bash
# Check all service status
docker-compose ps

# View service logs
docker-compose logs -f backend
docker-compose logs -f validator-agent

# Service health endpoints
curl http://localhost:8000/health
curl http://localhost:8000/api/v1/agents/scheduler/health
```

## 📁 Project Structure

```
krnl-onboarding-system/
├── backend/                    # Python FastAPI backend
│   ├── agents/                # Individual agent implementations
│   │   ├── validator_agent.py
│   │   ├── account_setup_agent.py
│   │   ├── scheduler_agent.py
│   │   ├── notifier_agent.py
│   │   └── mcp_manifests/     # MCP compliance manifests
│   ├── communication/         # A2A communication system
│   ├── tests/                 # Unit tests
│   ├── models.py              # Database models
│   ├── schemas.py             # Pydantic schemas
│   ├── database.py            # Database configuration
│   ├── orchestrator.py        # Workflow orchestration
│   ├── logging_system.py      # Audit and traceability
│   ├── main.py               # FastAPI application
│   └── requirements.txt       # Python dependencies
├── frontend/                  # HTML/CSS/JavaScript dashboard
│   ├── index.html            # Main dashboard page
│   ├── styles.css            # Responsive CSS styles  
│   ├── app.js                # JavaScript application logic
│   └── nginx.conf            # Nginx configuration
├── database/                  # Database initialization
│   └── init.sql              # Schema and initial setup
├── docker-compose.yml         # Multi-service orchestration
└── README.md                 # This documentation
```

## 🔧 Configuration

### Environment Variables

Create a `.env` file for custom configuration:

```bash
# Database Configuration
DATABASE_URL=postgresql://postgres:password@postgres:5432/krnl_onboarding
POSTGRES_DB=krnl_onboarding
POSTGRES_USER=postgres
POSTGRES_PASSWORD=password

# Redis Configuration  
REDIS_URL=redis://redis:6379

# Application Settings
ENVIRONMENT=development
API_BASE_URL=http://localhost:8000

# Google Calendar (optional)
GOOGLE_CALENDAR_CREDENTIALS=path/to/credentials.json

# Notification Settings
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
EMAIL_USER=your-email@company.com
EMAIL_PASSWORD=your-password

SLACK_BOT_TOKEN=xoxb-your-slack-token
SLACK_CHANNEL=#hr-notifications
```

### Database Migration

For schema updates:
```bash
# Access database directly
docker-compose exec postgres psql -U postgres -d krnl_onboarding

# Run custom migrations
docker-compose exec backend python -c "from database import create_tables; create_tables()"
```

## 🔍 Monitoring & Observability

### System Health Monitoring
- **Agent Performance Metrics**: Success rates, execution times, error patterns
- **Workflow Analytics**: Completion rates, bottleneck identification
- **Database Monitoring**: Connection health, query performance
- **Resource Utilization**: Memory, CPU, and disk usage tracking

### Audit Trail Features
- **Complete Traceability**: Every action logged with timestamps and context
- **Cross-Agent Tracking**: Follow data through all workflow steps
- **Error Diagnostics**: Detailed error context and resolution guidance
- **Compliance Reporting**: Export audit data for regulatory requirements

### Performance Optimization
- **Database Indexing**: Optimized queries for large datasets
- **Caching Strategy**: Redis caching for frequently accessed data
- **Async Processing**: Non-blocking operations for better throughput
- **Resource Pooling**: Efficient connection and resource management

## 🚀 Production Deployment

### Scaling Considerations

For production deployment, consider:

1. **Database Scaling**: PostgreSQL replication and connection pooling
2. **Agent Scaling**: Multiple instances of each agent type
3. **Load Balancing**: Multiple backend API instances
4. **Message Queue Clustering**: Redis cluster for high availability
5. **Monitoring Integration**: Prometheus, Grafana, ELK stack
6. **Security Hardening**: SSL/TLS, authentication, network policies

### Deployment Patterns

```bash
# Production deployment with scaling
docker-compose -f docker-compose.prod.yml up -d

# Kubernetes deployment
kubectl apply -f k8s/

# Cloud deployment (AWS/Azure/GCP)
terraform apply -var-file="production.tfvars"
```

## 🤝 Contributing

### Development Workflow

1. **Fork and Clone**: Create your development branch
2. **Environment Setup**: Use development Docker compose
3. **Feature Development**: Implement features with tests
4. **Testing**: Run comprehensive test suite
5. **Documentation**: Update README and API docs  
6. **Pull Request**: Submit for review with detailed description

### Code Quality Standards

- **Python**: Follow PEP 8 style guidelines
- **Testing**: Minimum 80% code coverage required
- **Documentation**: Docstrings for all public methods
- **Type Hints**: Use type annotations throughout
- **Error Handling**: Comprehensive exception handling
- **Logging**: Structured logging with contextual information

## 📈 Roadmap & Future Enhancements

### Planned Features

- **Advanced Agent AI**: LLM integration for intelligent decision making
- **Real-time Dashboards**: WebSocket-based live updates  
- **Mobile Application**: React Native app for mobile management
- **Advanced Analytics**: Machine learning for workflow optimization
- **Multi-tenant Support**: Organization isolation and management
- **Integration Hub**: Connectors for popular HR systems
- **Workflow Designer**: Visual workflow creation and customization

### Architecture Evolution

- **Event Sourcing**: Complete event-driven architecture
- **CQRS Implementation**: Command/query responsibility segregation
- **Distributed Tracing**: OpenTelemetry integration
- **Service Mesh**: Istio for advanced traffic management
- **GitOps Deployment**: ArgoCD for continuous deployment

## 🛟 Support & Troubleshooting

### Common Issues

**Database Connection Issues**
```bash
# Check database status
docker-compose logs postgres

# Reset database
docker-compose down -v
docker-compose up postgres -d
```

**Agent Communication Problems**
```bash
# Check Redis connectivity
docker-compose logs redis

# Restart agent services
docker-compose restart validator-agent account-agent scheduler-agent notifier-agent
```

**Frontend Not Loading**
```bash
# Check frontend service
docker-compose logs frontend

# Verify API connectivity
curl http://localhost:8000/health
```

### Debug Mode

Enable debug logging:
```bash
# Set debug environment
export ENVIRONMENT=debug

# View detailed logs
docker-compose logs -f --tail=100 backend
```

### Performance Issues

Monitor system resources:
```bash
# System resource usage
docker stats

# Database performance
docker-compose exec postgres pg_stat_activity

# Redis memory usage
docker-compose exec redis redis-cli info memory
```

## 📄 License & Credits

This project is developed for demonstration of advanced multi-agent system architectures, MCP compliance, and A2A communication patterns.

**Technologies Used:**
- **Backend**: FastAPI, SQLAlchemy, PostgreSQL, Redis, Pydantic
- **Frontend**: HTML5, CSS3, JavaScript (ES6+), Font Awesome
- **Infrastructure**: Docker, Docker Compose, Nginx
- **Testing**: pytest, asyncio
- **Architecture**: MCP, A2A, Microservices, Event-driven design

---

For questions, issues, or contributions, please open a GitHub issue or contact the development team.

**Happy Onboarding! 🎉**