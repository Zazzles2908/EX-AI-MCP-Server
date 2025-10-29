-- Supabase Universal File Hub - Row Level Security Policies (Development Version)
-- Date: 2025-10-30
-- EXAI Consultation ID: bbfac185-ce22-4140-9b30-b3fda4c362d9
-- Modified for single-user development environment (service role access)

-- ============================================================================
-- ENABLE ROW LEVEL SECURITY
-- ============================================================================

ALTER TABLE public.file_operations ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.file_metadata ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.users ENABLE ROW LEVEL SECURITY;

-- ============================================================================
-- USERS TABLE POLICIES (Development - allow service role full access)
-- ============================================================================

DROP POLICY IF EXISTS "Service role can manage users" ON public.users;
CREATE POLICY "Service role can manage users" 
  ON public.users
  FOR ALL
  USING (true)
  WITH CHECK (true);

-- ============================================================================
-- FILE_OPERATIONS TABLE POLICIES (Development - allow service role full access)
-- ============================================================================

DROP POLICY IF EXISTS "Service role can manage file operations" ON public.file_operations;
CREATE POLICY "Service role can manage file operations" 
  ON public.file_operations
  FOR ALL
  USING (true)
  WITH CHECK (true);

-- ============================================================================
-- FILE_METADATA TABLE POLICIES (Development - allow service role full access)
-- ============================================================================

DROP POLICY IF EXISTS "Service role can manage file metadata" ON public.file_metadata;
CREATE POLICY "Service role can manage file metadata" 
  ON public.file_metadata
  FOR ALL
  USING (true)
  WITH CHECK (true);

-- ============================================================================
-- NOTES ON DEVELOPMENT POLICIES
-- ============================================================================

-- These policies allow full access when using the service role key
-- Service role key bypasses RLS by default, but we enable RLS for consistency
-- 
-- For production with auth.users, replace with user-specific policies:
-- USING (auth.uid() = user_id)
-- WITH CHECK (auth.uid() = user_id)

-- ============================================================================
-- COMPLETION MESSAGE
-- ============================================================================

DO $$
BEGIN
  RAISE NOTICE 'Row Level Security policies (DEV) created successfully!';
  RAISE NOTICE 'All tables: Service role has full access';
  RAISE NOTICE 'RLS enabled for: users, file_operations, file_metadata';
  RAISE NOTICE '';
  RAISE NOTICE 'Development mode: Using service role key for all operations';
  RAISE NOTICE 'Storage bucket policies: Not needed (service role bypasses)';
  RAISE NOTICE '';
  RAISE NOTICE 'Next step: Create storage buckets and test setup';
END $$;

