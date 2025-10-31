-- Supabase Universal File Hub - Row Level Security Policies
-- Date: 2025-10-30
-- EXAI Consultation ID: bbfac185-ce22-4140-9b30-b3fda4c362d9

-- ============================================================================
-- ENABLE ROW LEVEL SECURITY
-- ============================================================================

ALTER TABLE public.file_operations ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.file_metadata ENABLE ROW LEVEL SECURITY;

-- ============================================================================
-- FILE_OPERATIONS TABLE POLICIES
-- ============================================================================

-- Policy: Users can view their own file operations
DROP POLICY IF EXISTS "Users can view their own file operations" ON public.file_operations;
CREATE POLICY "Users can view their own file operations" 
  ON public.file_operations
  FOR SELECT 
  USING (auth.uid() = user_id);

-- Policy: Users can insert their own file operations
DROP POLICY IF EXISTS "Users can insert their own file operations" ON public.file_operations;
CREATE POLICY "Users can insert their own file operations" 
  ON public.file_operations
  FOR INSERT 
  WITH CHECK (auth.uid() = user_id);

-- Policy: Users can update their own file operations
DROP POLICY IF EXISTS "Users can update their own file operations" ON public.file_operations;
CREATE POLICY "Users can update their own file operations" 
  ON public.file_operations
  FOR UPDATE 
  USING (auth.uid() = user_id);

-- Policy: Users can delete their own file operations
DROP POLICY IF EXISTS "Users can delete their own file operations" ON public.file_operations;
CREATE POLICY "Users can delete their own file operations" 
  ON public.file_operations
  FOR DELETE 
  USING (auth.uid() = user_id);

-- ============================================================================
-- FILE_METADATA TABLE POLICIES
-- ============================================================================

-- Policy: Users can view their own file metadata
DROP POLICY IF EXISTS "Users can view their own file metadata" ON public.file_metadata;
CREATE POLICY "Users can view their own file metadata" 
  ON public.file_metadata
  FOR SELECT 
  USING (auth.uid() = user_id);

-- Policy: Users can insert their own file metadata
DROP POLICY IF EXISTS "Users can insert their own file metadata" ON public.file_metadata;
CREATE POLICY "Users can insert their own file metadata" 
  ON public.file_metadata
  FOR INSERT 
  WITH CHECK (auth.uid() = user_id);

-- Policy: Users can update their own file metadata
DROP POLICY IF EXISTS "Users can update their own file metadata" ON public.file_metadata;
CREATE POLICY "Users can update their own file metadata" 
  ON public.file_metadata
  FOR UPDATE 
  USING (auth.uid() = user_id);

-- Policy: Users can delete their own file metadata
DROP POLICY IF EXISTS "Users can delete their own file metadata" ON public.file_metadata;
CREATE POLICY "Users can delete their own file metadata" 
  ON public.file_metadata
  FOR DELETE 
  USING (auth.uid() = user_id);

-- ============================================================================
-- STORAGE BUCKET POLICIES - USER-FILES
-- ============================================================================

-- Policy: Users can upload their own files to user-files bucket
DROP POLICY IF EXISTS "Users can upload to user-files" ON storage.objects;
CREATE POLICY "Users can upload to user-files" 
  ON storage.objects
  FOR INSERT 
  WITH CHECK (
    bucket_id = 'user-files' AND 
    auth.uid()::text = (storage.foldername(name))[1]
  );

-- Policy: Users can view their own files in user-files bucket
DROP POLICY IF EXISTS "Users can view user-files" ON storage.objects;
CREATE POLICY "Users can view user-files" 
  ON storage.objects
  FOR SELECT 
  USING (
    bucket_id = 'user-files' AND 
    auth.uid()::text = (storage.foldername(name))[1]
  );

-- Policy: Users can update their own files in user-files bucket
DROP POLICY IF EXISTS "Users can update user-files" ON storage.objects;
CREATE POLICY "Users can update user-files" 
  ON storage.objects
  FOR UPDATE 
  USING (
    bucket_id = 'user-files' AND 
    auth.uid()::text = (storage.foldername(name))[1]
  );

-- Policy: Users can delete their own files in user-files bucket
DROP POLICY IF EXISTS "Users can delete user-files" ON storage.objects;
CREATE POLICY "Users can delete user-files" 
  ON storage.objects
  FOR DELETE 
  USING (
    bucket_id = 'user-files' AND 
    auth.uid()::text = (storage.foldername(name))[1]
  );

-- ============================================================================
-- STORAGE BUCKET POLICIES - RESULTS
-- ============================================================================

-- Policy: Users can upload to results bucket
DROP POLICY IF EXISTS "Users can upload to results" ON storage.objects;
CREATE POLICY "Users can upload to results" 
  ON storage.objects
  FOR INSERT 
  WITH CHECK (
    bucket_id = 'results' AND 
    auth.uid()::text = (storage.foldername(name))[1]
  );

-- Policy: Users can view their own result files
DROP POLICY IF EXISTS "Users can view results" ON storage.objects;
CREATE POLICY "Users can view results" 
  ON storage.objects
  FOR SELECT 
  USING (
    bucket_id = 'results' AND 
    auth.uid()::text = (storage.foldername(name))[1]
  );

-- Policy: Users can update their own result files
DROP POLICY IF EXISTS "Users can update results" ON storage.objects;
CREATE POLICY "Users can update results" 
  ON storage.objects
  FOR UPDATE 
  USING (
    bucket_id = 'results' AND 
    auth.uid()::text = (storage.foldername(name))[1]
  );

-- Policy: Users can delete their own result files
DROP POLICY IF EXISTS "Users can delete results" ON storage.objects;
CREATE POLICY "Users can delete results" 
  ON storage.objects
  FOR DELETE 
  USING (
    bucket_id = 'results' AND 
    auth.uid()::text = (storage.foldername(name))[1]
  );

-- ============================================================================
-- STORAGE BUCKET POLICIES - GENERATED-FILES
-- ============================================================================

-- Policy: Users can upload to generated-files bucket
DROP POLICY IF EXISTS "Users can upload to generated-files" ON storage.objects;
CREATE POLICY "Users can upload to generated-files" 
  ON storage.objects
  FOR INSERT 
  WITH CHECK (
    bucket_id = 'generated-files' AND 
    auth.uid()::text = (storage.foldername(name))[1]
  );

-- Policy: Users can view their own generated files
DROP POLICY IF EXISTS "Users can view generated-files" ON storage.objects;
CREATE POLICY "Users can view generated-files" 
  ON storage.objects
  FOR SELECT 
  USING (
    bucket_id = 'generated-files' AND 
    auth.uid()::text = (storage.foldername(name))[1]
  );

-- Policy: Users can update their own generated files
DROP POLICY IF EXISTS "Users can update generated-files" ON storage.objects;
CREATE POLICY "Users can update generated-files" 
  ON storage.objects
  FOR UPDATE 
  USING (
    bucket_id = 'generated-files' AND 
    auth.uid()::text = (storage.foldername(name))[1]
  );

-- Policy: Users can delete their own generated files
DROP POLICY IF EXISTS "Users can delete generated-files" ON storage.objects;
CREATE POLICY "Users can delete generated-files" 
  ON storage.objects
  FOR DELETE 
  USING (
    bucket_id = 'generated-files' AND 
    auth.uid()::text = (storage.foldername(name))[1]
  );

-- ============================================================================
-- SERVICE ROLE BYPASS (for server-side operations)
-- ============================================================================

-- Note: Service role key bypasses RLS automatically
-- No additional policies needed for service role operations

-- ============================================================================
-- COMPLETION MESSAGE
-- ============================================================================

DO $$
BEGIN
  RAISE NOTICE 'Row Level Security policies created successfully!';
  RAISE NOTICE 'Database table policies: 8 policies (4 per table)';
  RAISE NOTICE 'Storage bucket policies: 12 policies (4 per bucket)';
  RAISE NOTICE 'Total policies: 20';
  RAISE NOTICE '';
  RAISE NOTICE 'Security features enabled:';
  RAISE NOTICE '  - User isolation (users can only access their own data)';
  RAISE NOTICE '  - Folder-based storage isolation';
  RAISE NOTICE '  - Service role bypass for server operations';
  RAISE NOTICE '';
  RAISE NOTICE 'Next step: Configure environment variables and test the setup';
END $$;

