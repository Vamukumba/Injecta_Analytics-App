import { createClient } from '@supabase/supabase-client'

// 1. Pull the keys securely from your new .env file
const supabaseUrl = import.meta.env.VITE_SUPABASE_URL
const supabaseAnonKey = import.meta.env.VITE_SUPABASE_ANON_KEY

// 2. Initialize the Supabase client
export const supabase = createClient(supabaseUrl, supabaseAnonKey)