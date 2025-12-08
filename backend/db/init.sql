CREATE EXTENSION IF NOT EXISTS pgcrypto;

CREATE TABLE models (
  id               UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  model            TEXT NOT NULL,         -- openai/gemini/grok etc.
  version          TEXT NOT NULL,         -- gpt-4.1, grok-4-1-fast-reasoning etc.
  created_at       TIMESTAMPTZ DEFAULT now(),
  updated_at       TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE prompts (
  id               UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  title            TEXT NOT NULL,
  content          TEXT NOT NULL,
  description      TEXT,
  labels           JSONB DEFAULT '[]',
  created_at       TIMESTAMPTZ DEFAULT now(),
  updated_at       TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE templates (
  id               UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name             TEXT NOT NULL,
  description      TEXT,
  labels           JSONB DEFAULT '[]',
  schema           JSONB NOT NULL,           -- 폼/버튼/액션 등 템플릿 전체 정의(JSON Schema 형태)
  created_at       TIMESTAMPTZ DEFAULT now(),
  updated_at       TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE user_input (
  id               UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  template_id      UUID,
  model            TEXT NOT NULL,
  version          TEXT,
  prompt           TEXT,
  input_type       TEXT NOT NULL,         -- text | form
  input_text       TEXT,
  input_form       JSONB,
  created_at       TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_templates_labels_gin ON templates USING GIN (labels);
