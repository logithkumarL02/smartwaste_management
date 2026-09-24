-- ============================================================
-- SmartWaste — Supabase Database Schema
-- Run this in the Supabase SQL Editor (once, on a fresh project)
-- ============================================================

-- ── 1. Profiles ────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS public.profiles (
  id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id     UUID NOT NULL UNIQUE REFERENCES auth.users(id) ON DELETE CASCADE,
  display_name TEXT NOT NULL DEFAULT '',
  avatar_url  TEXT,
  created_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Index for fast user lookups
CREATE INDEX IF NOT EXISTS profiles_user_id_idx ON public.profiles (user_id);

-- ── 2. Predictions ─────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS public.predictions (
  id               UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id          UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  category         TEXT NOT NULL,
  confidence       FLOAT NOT NULL CHECK (confidence >= 0 AND confidence <= 1),
  is_uncertain     BOOLEAN NOT NULL DEFAULT false,
  recommendation   TEXT,
  hardware_command TEXT,
  source           TEXT NOT NULL CHECK (source IN ('upload', 'webcam')),
  model_version    TEXT,
  image_url        TEXT,
  created_at       TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Indexes for common query patterns
CREATE INDEX IF NOT EXISTS predictions_user_id_idx   ON public.predictions (user_id);
CREATE INDEX IF NOT EXISTS predictions_created_at_idx ON public.predictions (created_at DESC);
CREATE INDEX IF NOT EXISTS predictions_category_idx  ON public.predictions (category);
CREATE INDEX IF NOT EXISTS predictions_user_created_idx ON public.predictions (user_id, created_at DESC);

-- ── 3. Row Level Security ──────────────────────────────────────────────────
ALTER TABLE public.profiles   ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.predictions ENABLE ROW LEVEL SECURITY;

-- Profiles: users can only read and update their own row
CREATE POLICY "profiles_select_own" ON public.profiles
  FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "profiles_insert_own" ON public.profiles
  FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "profiles_update_own" ON public.profiles
  FOR UPDATE USING (auth.uid() = user_id);

-- Predictions: users can only read and insert their own rows
-- (no update/delete — predictions are immutable records)
CREATE POLICY "predictions_select_own" ON public.predictions
  FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "predictions_insert_own" ON public.predictions
  FOR INSERT WITH CHECK (auth.uid() = user_id);

-- ── 4. Auto-create profile on signup ──────────────────────────────────────
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER LANGUAGE plpgsql SECURITY DEFINER SET search_path = public AS $$
BEGIN
  INSERT INTO public.profiles (user_id, display_name)
  VALUES (
    NEW.id,
    COALESCE(NEW.raw_user_meta_data->>'display_name', split_part(NEW.email, '@', 1))
  )
  ON CONFLICT (user_id) DO NOTHING;
  RETURN NEW;
END;
$$;

DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;
CREATE TRIGGER on_auth_user_created
  AFTER INSERT ON auth.users
  FOR EACH ROW EXECUTE FUNCTION public.handle_new_user();

-- ── 5. Optional: Supabase Storage bucket for prediction images ─────────────
-- Run this only if STORE_IMAGES=true in your backend .env
-- INSERT INTO storage.buckets (id, name, public)
-- VALUES ('prediction-images', 'prediction-images', false)
-- ON CONFLICT DO NOTHING;
--
-- CREATE POLICY "storage_user_owns_image" ON storage.objects
--   FOR ALL USING (auth.uid()::text = (storage.foldername(name))[1]);
