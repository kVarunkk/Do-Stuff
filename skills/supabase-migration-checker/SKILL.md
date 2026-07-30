---
name: supabase-migration-checker
description: Validates Supabase database migration scripts for high-concurrency performance, missing indexes, and schema locking issues. Trigger when asked to review or write SQL migrations.
---

# Supabase Migration Guidelines

When reviewing or writing SQL migrations for Postgres/Supabase, strictly check for these 4 performance killers:

1. **Missing Foreign Key Indexes:**
   - Every `REFERENCES` constraint must have an accompanying `CREATE INDEX IF NOT EXISTS`.

2. **Blocking Table Locks:**
   - Prefer `CREATE INDEX CONCURRENTLY` over standard `CREATE INDEX`.
   - Never add non-nullable columns without default values on heavy tables.

3. **RLS Policy Overhead:**
   - Ensure Row Level Security policies wrap query functions in `auth.uid() = user_id` rather than joining against user tables inline where possible.

4. **Output Format:**
   - Provide a table with column headers: `Severity | Issue | Recommended SQL Fix`.