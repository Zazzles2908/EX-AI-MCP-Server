-- Create file_operations table
CREATE TABLE IF NOT EXISTS public.file_operations (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  file_id UUID REFERENCES storage.objects(id) ON DELETE CASCADE,
  operation_type TEXT NOT NULL CHECK (operation_type IN ('upload', 'download', 'process', 'delete', 'generate')),
  status TEXT NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'processing', 'completed', 'failed')),
  metadata JSONB DEFAULT '{}',
  error_message TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  completed_at TIMESTAMP WITH TIME ZONE
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_file_operations_user_id ON public.file_operations(user_id);
CREATE INDEX IF NOT EXISTS idx_file_operations_file_id ON public.file_operations(file_id);
CREATE INDEX IF NOT EXISTS idx_file_operations_status ON public.file_operations(status);

-- Grant permissions
GRANT SELECT, INSERT, UPDATE, DELETE ON public.file_operations TO authenticated;
