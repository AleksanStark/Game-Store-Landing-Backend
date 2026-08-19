CREATE TABLE IF NOT EXISTS products (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    price NUMERIC(10, 2) NOT NULL,
    category_id INT REFERENCES categories(id) ON DELETE SET NULL,
    condition TEXT NOT NULL CHECK (condition IN ('new', 'used')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
)