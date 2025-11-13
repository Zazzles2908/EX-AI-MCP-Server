import { serve } from "https://deno.land/std@0.168.0/http/server.ts"
import { createClient } from 'https://esm.sh/@supabase/supabase-js@2'

const corsHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type',
}

// Configuration
const EXAI_DAEMON_URL = Deno.env.get('EXAI_DAEMON_URL') || 'ws://host.docker.internal:8079';
const EXAI_AUTH_TOKEN = Deno.env.get('EXAI_AUTH_TOKEN') || 'test-token-12345';
const TIMEOUT_MS = parseInt(Deno.env.get('EXAI_TIMEOUT_MS') || '180000'); // Increased to 3 minutes for longer responses

serve(async (req) => {
  // Handle CORS preflight
  if (req.method === 'OPTIONS') {
    return new Response('ok', { headers: corsHeaders })
  }

  try {
    const { session_id, tool_name, prompt } = await req.json()

    // Validate input
    if (!session_id || !tool_name || !prompt) {
      throw new Error('Missing required fields: session_id, tool_name, prompt')
    }

    if (prompt.length > 10000) {
      throw new Error('Prompt too long (max 10,000 characters)')
    }

    // Connect to EXAI daemon with timeout
    const ws = await connectWithTimeout(EXAI_DAEMON_URL, TIMEOUT_MS);

    try {
      // Send hello message
      await sendMessage(ws, {
        op: 'hello',
        token: EXAI_AUTH_TOKEN
      });

      // Wait for hello_ack
      const helloAck = await receiveMessage(ws, TIMEOUT_MS);
      if (!helloAck.ok) {
        throw new Error('Authentication failed');
      }

      // Send tool call
      const requestId = crypto.randomUUID();
      await sendMessage(ws, {
        op: 'call_tool',
        request_id: requestId,
        name: tool_name,
        arguments: { prompt }
      });

      // Wait for call_tool_ack
      await receiveMessage(ws, TIMEOUT_MS);

      // Wait for call_tool_res
      const result = await receiveMessage(ws, TIMEOUT_MS);

      // Save to database
      const supabase = createClient(
        Deno.env.get('SUPABASE_URL') ?? '',
        Deno.env.get('SUPABASE_SERVICE_ROLE_KEY') ?? ''  // Use service role for database writes
      )

      // DEDUPLICATION FIX (2025-10-22): Generate idempotency keys to prevent duplicates
      const generateIdempotencyKey = (conversationId: string, role: string, content: string, timestamp: string): string => {
        const keyString = `${conversationId}:${role}:${content.trim()}:${timestamp}`;
        const encoder = new TextEncoder();
        const data = encoder.encode(keyString);
        return crypto.subtle.digest('SHA-256', data)
          .then(hash => Array.from(new Uint8Array(hash))
            .map(b => b.toString(16).padStart(2, '0'))
            .join(''));
      };

      const timestamp = new Date().toISOString();

      // Get or create conversation
      let conversation = await supabase
        .from('conversations')
        .select('id')
        .eq('session_id', session_id)
        .single();

      let conversationId: string;
      if (!conversation.data) {
        // Create new conversation
        const newConv = await supabase
          .from('conversations')
          .insert({
            session_id: session_id,
            continuation_id: session_id,  // Use session_id as continuation_id
            title: `EXAI Chat ${new Date().toLocaleDateString()}`,
            metadata: { tool_name, created_via: 'edge_function' }
          })
          .select('id')
          .single();
        conversationId = newConv.data.id;
      } else {
        conversationId = conversation.data.id;
      }

      // Save user message with idempotency key
      const userIdempotencyKey = await generateIdempotencyKey(conversationId, 'user', prompt, timestamp);
      await supabase.from('messages').insert({
        conversation_id: conversationId,
        role: 'user',
        content: prompt,
        metadata: { tool_name },
        idempotency_key: userIdempotencyKey
      });

      // Save assistant response with idempotency key
      const assistantTimestamp = new Date().toISOString();
      const assistantContent = result.content || 'No response';
      const assistantIdempotencyKey = await generateIdempotencyKey(conversationId, 'assistant', assistantContent, assistantTimestamp);
      await supabase.from('messages').insert({
        conversation_id: conversationId,
        role: 'assistant',
        content: assistantContent,
        metadata: {
          tool_name,
          model_used: result.metadata?.model_used,
          provider_used: result.metadata?.provider_used,
          tokens_in: result.metadata?.tokens_in,
          tokens_out: result.metadata?.tokens_out,
          ...result.metadata
        },
        idempotency_key: assistantIdempotencyKey
      });

      // Update conversation timestamp
      await supabase
        .from('conversations')
        .update({ updated_at: new Date().toISOString() })
        .eq('id', conversationId)

      return new Response(
        JSON.stringify({
          content: result.content,
          metadata: result.metadata,
        }),
        { headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
      )

    } finally {
      ws.close();
    }

  } catch (error) {
    console.error('Error:', error);
    return new Response(
      JSON.stringify({ error: error.message }),
      { 
        status: 500,
        headers: { ...corsHeaders, 'Content-Type': 'application/json' }
      }
    )
  }
})

// Helper: Connect with timeout
async function connectWithTimeout(url: string, timeout: number): Promise<WebSocket> {
  return new Promise((resolve, reject) => {
    const ws = new WebSocket(url);
    const timer = setTimeout(() => {
      ws.close();
      reject(new Error('Connection timeout'));
    }, timeout);

    ws.onopen = () => {
      clearTimeout(timer);
      resolve(ws);
    };

    ws.onerror = (error) => {
      clearTimeout(timer);
      reject(error);
    };
  });
}

// Helper: Send message
async function sendMessage(ws: WebSocket, message: any): Promise<void> {
  ws.send(JSON.stringify(message));
}

// Helper: Receive message with timeout
async function receiveMessage(ws: WebSocket, timeout: number): Promise<any> {
  return new Promise((resolve, reject) => {
    const timer = setTimeout(() => {
      reject(new Error('Receive timeout'));
    }, timeout);

    ws.onmessage = (event) => {
      clearTimeout(timer);
      resolve(JSON.parse(event.data));
    };

    ws.onerror = (error) => {
      clearTimeout(timer);
      reject(error);
    };
  });
}

