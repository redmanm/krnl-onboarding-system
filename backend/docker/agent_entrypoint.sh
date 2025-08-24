#!/bin/bash

# Agent entrypoint script
set -e

# Wait for database to be ready
echo "Waiting for database..."
until python -c "
import psycopg2
import os
import sys
try:
    conn = psycopg2.connect(os.getenv('DATABASE_URL'))
    conn.close()
    print('Database is ready!')
except Exception as e:
    print(f'Database not ready: {e}')
    sys.exit(1)
"; do
  echo "Database is unavailable - sleeping"
  sleep 2
done

# Wait for Redis to be ready
echo "Waiting for Redis..."
until python -c "
import redis
import os
import sys
try:
    r = redis.from_url(os.getenv('REDIS_URL', 'redis://redis:6379'))
    r.ping()
    print('Redis is ready!')
except Exception as e:
    print(f'Redis not ready: {e}')
    sys.exit(1)
"; do
  echo "Redis is unavailable - sleeping"
  sleep 2
done

# Get agent type from environment variable
AGENT_TYPE=${AGENT_TYPE:-"validator"}

echo "Starting ${AGENT_TYPE} agent..."

# Run the specific agent based on type
case $AGENT_TYPE in
  "validator")
    python -c "
import asyncio
from agents.validator_agent import ValidatorAgent
from communication.a2a_system import A2ACommunicationBus
import os

async def run_validator():
    bus = A2ACommunicationBus(os.getenv('REDIS_URL'))
    agent = ValidatorAgent()
    print('Validator agent started and listening for messages...')
    # In a real implementation, this would listen for messages
    while True:
        await asyncio.sleep(10)
        print('Validator agent heartbeat...')

asyncio.run(run_validator())
    "
    ;;
  "account_setup")
    python -c "
import asyncio
from agents.account_setup_agent import AccountSetupAgent
from communication.a2a_system import A2ACommunicationBus
import os

async def run_account_setup():
    bus = A2ACommunicationBus(os.getenv('REDIS_URL'))
    agent = AccountSetupAgent(bus)
    print('Account Setup agent started and listening for messages...')
    # In a real implementation, this would listen for messages
    while True:
        await asyncio.sleep(10)
        print('Account Setup agent heartbeat...')

asyncio.run(run_account_setup())
    "
    ;;
  "scheduler")
    python -c "
import asyncio
from agents.scheduler_agent import SchedulerAgent
from communication.a2a_system import A2ACommunicationBus
import os

async def run_scheduler():
    bus = A2ACommunicationBus(os.getenv('REDIS_URL'))
    agent = SchedulerAgent()
    print('Scheduler agent started and listening for messages...')
    # In a real implementation, this would listen for messages
    while True:
        await asyncio.sleep(10)
        print('Scheduler agent heartbeat...')

asyncio.run(run_scheduler())
    "
    ;;
  "notifier")
    python -c "
import asyncio
from agents.notifier_agent import NotifierAgent
from communication.a2a_system import A2ACommunicationBus
import os

async def run_notifier():
    bus = A2ACommunicationBus(os.getenv('REDIS_URL'))
    agent = NotifierAgent()
    print('Notifier agent started and listening for messages...')
    # In a real implementation, this would listen for messages
    while True:
        await asyncio.sleep(10)
        print('Notifier agent heartbeat...')

asyncio.run(run_notifier())
    "
    ;;
  *)
    echo "Unknown agent type: $AGENT_TYPE"
    exit 1
    ;;
esac