CREATE TABLE IF NOT EXISTS guests (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    last_seen_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
 
CREATE TABLE IF NOT EXISTS chat_messages (
    id SERIAL PRIMARY KEY,
    guest_id UUID NOT NULL REFERENCES guests(id) ON DELETE CASCADE,
    sender TEXT NOT NULL CHECK (sender IN ('guest', 'admin')),
    body TEXT NOT NULL,
    read_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
 
CREATE INDEX IF NOT EXISTS idx_chat_messages_guest_id ON chat_messages(guest_id, created_at);
 
-- gen_random_uuid() требует расширения pgcrypto — включаем один раз
CREATE EXTENSION IF NOT EXISTS pgcrypto;
 