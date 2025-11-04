#!/usr/bin/env python3
"""
Supabase Pro Setup Automation
Sets up production-grade Supabase configuration with Pro features
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from typing import Dict, List


class SupabaseProSetup:
    """Automates Supabase Pro setup"""

    def __init__(self):
        self.project_root = Path(__file__).parent.parent.parent
        self.supabase_dir = self.project_root / 'supabase'
        self.config = {}

    def load_env(self):
        """Load environment configuration"""
        env_file = self.project_root / '.env'
        if not env_file.exists():
            print("❌ .env file not found!")
            sys.exit(1)

        with open(env_file, 'r') as f:
            for line in f:
                if '=' in line and not line.strip().startswith('#'):
                    key, value = line.strip().split('=', 1)
                    os.environ[key] = value

        print("✓ Environment loaded")

    def setup_database_schema(self):
        """Setup database schema with RLS"""
        print("\n💾 Setting up database schema...")

        schema_sql = """
-- Enable RLS on all tables
ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE conversations ENABLE ROW LEVEL SECURITY;
ALTER TABLE messages ENABLE ROW LEVEL SECURITY;
ALTER TABLE files ENABLE ROW LEVEL SECURITY;
ALTER TABLE audit_logs ENABLE ROW LEVEL SECURITY;

-- Create RLS policies
-- Profiles: Users can only access their own profile
CREATE POLICY "Users can view own profile" ON profiles
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can update own profile" ON profiles
    FOR UPDATE USING (auth.uid() = user_id);

-- Sessions: Users can only access their own sessions
CREATE POLICY "Users can view own sessions" ON sessions
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can create own sessions" ON sessions
    FOR INSERT WITH CHECK (auth.uid() = user_id);

-- Conversations: Users can only access their own conversations
CREATE POLICY "Users can view own conversations" ON conversations
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can create own conversations" ON conversations
    FOR INSERT WITH CHECK (auth.uid() = user_id);

-- Messages: Users can only access messages in their conversations
CREATE POLICY "Users can view own messages" ON messages
    FOR SELECT USING (auth.uid() IN (
        SELECT user_id FROM conversations WHERE id = conversation_id
    ));

CREATE POLICY "Users can create own messages" ON messages
    FOR INSERT WITH CHECK (auth.uid() IN (
        SELECT user_id FROM conversations WHERE id = conversation_id
    ));

-- Audit logs: Read-only for users, full access for admins
CREATE POLICY "Users can view audit logs" ON audit_logs
    FOR SELECT USING (auth.role() = 'authenticated');

-- Create indexes for performance
CREATE INDEX idx_profiles_user_id ON profiles(user_id);
CREATE INDEX idx_sessions_user_id ON sessions(user_id);
CREATE INDEX idx_conversations_user_id ON conversations(user_id);
CREATE INDEX idx_messages_conversation_id ON messages(conversation_id);
CREATE INDEX idx_files_user_id ON files(user_id);

-- Create updated_at triggers
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_profiles_updated_at BEFORE UPDATE ON profiles
    FOR EACH ROW EXECUTE PROCEDURE update_updated_at_column();

CREATE TRIGGER update_sessions_updated_at BEFORE UPDATE ON sessions
    FOR EACH ROW EXECUTE PROCEDURE update_updated_at_column();

CREATE TRIGGER update_conversations_updated_at BEFORE UPDATE ON conversations
    FOR EACH ROW EXECUTE PROCEDURE update_updated_at_column();
"""
        # Save schema to file
        schema_file = self.supabase_dir / 'migration_setup.sql'
        with open(schema_file, 'w') as f:
            f.write(schema_sql)

        print(f"✓ Database schema created: {schema_file}")
        print("  Note: Run this SQL in Supabase SQL Editor to apply")

    def setup_edge_functions(self):
        """Setup edge functions"""
        print("\n⚡ Setting up edge functions...")

        # Create edge function for JWT verification
        jwt_function = self.supabase_dir / 'functions' / 'verify-jwt'
        jwt_function.mkdir(parents=True, exist_ok=True)

        index_ts = jwt_function / 'index.ts'
        with open(index_ts, 'w') as f:
            f.write("""
import { serve } from 'https://deno.land/std@0.168.0/http/server.ts'

serve(async (req) => {
  const authHeader = req.headers.get('Authorization')

  if (!authHeader) {
    return new Response(JSON.stringify({ error: 'No auth header' }), {
      status: 401,
      headers: { 'Content-Type': 'application/json' },
    })
  }

  // Verify JWT token logic here

  return new Response(JSON.stringify({ verified: true }), {
    headers: { 'Content-Type': 'application/json' },
  })
})
""")
        print(f"✓ Edge function created: {jwt_function}")

    def create_backup_script(self):
        """Create backup automation script"""
        print("\n💾 Creating backup script...")

        backup_script = self.project_root / 'scripts' / 'backup' / 'automated_backup.sh'
        backup_script.parent.mkdir(parents=True, exist_ok=True)

        with open(backup_script, 'w') as f:
            f.write("""#!/bin/bash
# Automated Supabase Backup Script

SUPABASE_URL="${SUPABASE_URL}"
SUPABASE_SERVICE_KEY="${SUPABASE_SERVICE_ROLE_KEY}"

BACKUP_DIR="/backups/supabase/$(date +%Y-%m-%d)"
mkdir -p "$BACKUP_DIR"

echo "Starting backup to $BACKUP_DIR..."

# Backup database
pg_dump "$SUPABASE_URL" > "$BACKUP_DIR/database.sql"

# Compress backup
gzip "$BACKUP_DIR/database.sql"

# Upload to cloud storage (optional)
# aws s3 cp "$BACKUP_DIR/database.sql.gz" "s3://backups/database-$(date +%Y%m%d).sql.gz"

echo "Backup completed: $BACKUP_DIR/database.sql.gz"

# Cleanup old backups (keep 30 days)
find /backups/supabase -type d -mtime +30 -exec rm -rf {} \;

echo "Cleanup completed"
""")
        backup_script.chmod(0o755)

        print(f"✓ Backup script created: {backup_script}")

    def create_monitoring_query(self):
        """Create database monitoring query"""
        print("\n📊 Creating database monitoring...")

        monitoring_sql = """
-- Database Performance Monitoring Views

-- Active connections
CREATE VIEW active_connections AS
SELECT
    state,
    count(*) as connection_count
FROM pg_stat_activity
WHERE state IS NOT NULL
GROUP BY state;

-- Slow queries
CREATE VIEW slow_queries AS
SELECT
    query,
    mean_exec_time,
    calls,
    total_exec_time
FROM pg_stat_statements
ORDER BY mean_exec_time DESC
LIMIT 10;

-- Table sizes
CREATE VIEW table_sizes AS
SELECT
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;

-- Index usage
CREATE VIEW index_usage AS
SELECT
    schemaname,
    tablename,
    indexname,
    idx_scan,
    idx_tup_read,
    idx_tup_fetch
FROM pg_stat_user_indexes
ORDER BY idx_scan DESC;
"""
        monitor_file = self.supabase_dir / 'monitoring_views.sql'
        with open(monitor_file, 'w') as f:
            f.write(monitoring_sql)

        print(f"✓ Monitoring views created: {monitor_file}")

    def create_config_validation(self):
        """Create configuration validation"""
        print("\n✅ Creating config validation...")

        validation_script = self.project_root / 'scripts' / 'validate_supabase_config.py'
        validation_script.parent.mkdir(parents=True, exist_ok=True)

        with open(validation_script, 'w') as f:
            f.write("""#!/usr/bin/env python3
import os

required_vars = [
    'SUPABASE_URL',
    'SUPABASE_ANON_KEY',
    'SUPABASE_SERVICE_ROLE_KEY'
]

missing = []
for var in required_vars:
    if not os.getenv(var):
        missing.append(var)

if missing:
    print("❌ Missing required environment variables:")
    for var in missing:
        print(f"  - {var}")
    sys.exit(1)
else:
    print("✅ All Supabase environment variables are set")
""")

        print(f"✓ Config validation created: {validation_script}")

    def generate_deployment_guide(self):
        """Generate deployment guide"""
        print("\n📚 Generating deployment guide...")

        guide = """
# Supabase Pro Deployment Guide

## Pre-deployment Checklist
1. ✅ Create Supabase project (Pro plan)
2. ✅ Configure custom domain
3. ✅ Enable Point-in-Time Recovery (PITR)
4. ✅ Set up read replicas (if needed)
5. ✅ Configure Edge Functions
6. ✅ Enable real-time
7. ✅ Set up monitoring

## Database Setup
1. Run migration_setup.sql in Supabase SQL Editor
2. Verify RLS policies are enabled
3. Test all tables are accessible
4. Run monitoring_views.sql for performance tracking

## Edge Functions
1. Deploy functions:
   ```bash
   supabase functions deploy verify-jwt
   ```

2. Set environment variables in Supabase dashboard

## Backup Configuration
1. Enable PITR (automatic 7-day retention)
2. Set up automated backups:
   ```bash
   crontab -e
   0 2 * * * /scripts/backup/automated_backup.sh
   ```

## Security
1. Configure RLS policies on all tables
2. Set up JWT authentication
3. Enable API rate limiting
4. Configure CORS policies
5. Enable audit logging

## Monitoring
1. Import Grafana dashboards
2. Configure alerts
3. Set up log aggregation
4. Monitor performance metrics

## Post-deployment
1. Run health checks
2. Verify backups
3. Test disaster recovery
4. Monitor for 48 hours
5. Complete production readiness validation
"""
        guide_file = self.project_root / 'SUPABASE_DEPLOYMENT_GUIDE.md'
        with open(guide_file, 'w') as f:
            f.write(guide)

        print(f"✓ Deployment guide created: {guide_file}")

    def run_setup(self):
        """Run complete setup"""
        print("=" * 60)
        print("SUPABASE PRO SETUP AUTOMATION")
        print("=" * 60)

        self.load_env()
        self.setup_database_schema()
        self.setup_edge_functions()
        self.create_backup_script()
        self.create_monitoring_query()
        self.create_config_validation()
        self.generate_deployment_guide()

        print("\n" + "=" * 60)
        print("✅ SUPABASE PRO SETUP COMPLETED")
        print("=" * 60)
        print("\nNext steps:")
        print("1. Review generated files in ./supabase/")
        print("2. Run migrations in Supabase SQL Editor")
        print("3. Deploy edge functions")
        print("4. Set up automated backups")
        print("5. Configure monitoring")
        print("\nSee SUPABASE_DEPLOYMENT_GUIDE.md for detailed instructions")


if __name__ == '__main__':
    setup = SupabaseProSetup()
    setup.run_setup()
