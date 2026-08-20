-- seed_products.sql
-- Заполняет categories, products, product_images данными из моков.
-- Безопасно перезапускать: повторный запуск не создаст дублей
-- (проверка через NOT EXISTS вместо ON CONFLICT, чтобы не зависеть
-- от того, есть ли у тебя уникальные constraints на этих таблицах).

BEGIN;

-- ========== 1. КАТЕГОРИИ ==========
-- "featured" и "all" из мока — не реальные категории, а ярлыки фильтра на фронте,
-- поэтому их здесь нет.

INSERT INTO categories (name)
SELECT v.name
FROM (VALUES
    ('PlayStation'),
    ('Игры'),
    ('Смартфоны'),
    ('Dyson')
) AS v(name)
WHERE NOT EXISTS (
    SELECT 1 FROM categories c WHERE c.name = v.name
);

-- ========== 2. ТОВАРЫ ==========
-- price взят как чистое число из "$900 и выше" -> 900 и т.п.
-- "по запросу" (PlayStation-аккаунт) поставлен как 0 — поправь вручную в админке,
-- если price NOT NULL не должен означать "бесплатно".

INSERT INTO products (name, price, category_id, condition)
SELECT v.name, v.price, c.id, v.condition
FROM (VALUES
    ('PS5 Pro',                              900.00, 'new',  'PlayStation'),
    ('PS5 Pro',                              780.00, 'used', 'PlayStation'),
    ('PS5 Slim',                             400.00, 'used', 'PlayStation'),
    ('PlayStation VR2',                      400.00, 'new',  'PlayStation'),
    ('PlayStation VR2',                      400.00, 'used', 'PlayStation'),
    ('PS5 Disc Edition',                     400.00, 'new',  'PlayStation'),
    ('PS5 Disc Edition',                     400.00, 'used', 'PlayStation'),
    ('PS5 Slim Disc Edition (новая)',        600.00, 'new',  'PlayStation'),
    ('PS5 Slim Disc Edition (Б/У)',          400.00, 'used', 'PlayStation'),
    ('PS5 Slim Digital Edition (новая)',     600.00, 'new',  'PlayStation'),
    ('PS5 Slim Digital Edition (Б/У)',       400.00, 'used', 'PlayStation'),
    ('PS4 Slim',                             150.00, 'used', 'PlayStation'),
    ('PS4 Pro',                              220.00, 'new',  'PlayStation'),
    ('PS4 Pro',                              220.00, 'used', 'PlayStation'),

    ('Ghost of Tsushima (диск)',              45.00, 'new',  'Игры'),
    ('The Last of Us Part II (диск)',         25.00, 'used', 'Игры'),
    ('PlayStation-аккаунт (набор игр)',        0.00, 'new',  'Игры'), -- было "по запросу"
    ('EA Sports FC 25 (диск)',                20.00, 'used', 'Игры'),

    ('iPhone 17 Pro',                       1050.00, 'new',  'Смартфоны'),
    ('iPhone 15',                            520.00, 'used', 'Смартфоны'),
    ('Samsung Galaxy S25',                   610.00, 'used', 'Смартфоны'),
    ('Samsung Galaxy S25 Ultra',             950.00, 'new',  'Смартфоны'),

    ('Dyson Airwrap',                        430.00, 'new',  'Dyson'),
    ('Dyson V15 (пылесос)',                  310.00, 'used', 'Dyson'),
    ('Dyson Supersonic',                     390.00, 'new',  'Dyson')
) AS v(name, price, condition, category_name)
JOIN categories c ON c.name = v.category_name
WHERE NOT EXISTS (
    SELECT 1 FROM products p WHERE p.name = v.name AND p.condition = v.condition
);

-- ========== 3. ФОТО ТОВАРОВ ==========
-- Пары (name, condition) уникальны по всему списку выше, поэтому JOIN
-- по ним однозначно находит нужный товар даже при повторяющихся именах
-- ("PS5 Pro" встречается дважды — new и used).

INSERT INTO product_images (product_id, path, position)
SELECT p.id, v.img, 0
FROM (VALUES
    ('PS5 Pro',                              'new',  '/assets/ps5-pro.jpeg'),
    ('PS5 Pro',                              'used', '/assets/ps5-pro.jpeg'),
    ('PS5 Slim',                             'used', '/assets/ps5-digital-edition.jpeg'),
    ('PlayStation VR2',                      'new',  '/assets/ps-vr-2.jpeg'),
    ('PlayStation VR2',                      'used', '/assets/ps-vr-2.jpeg'),
    ('PS5 Disc Edition',                     'new',  '/assets/ps5-disc-edition.jpeg'),
    ('PS5 Disc Edition',                     'used', '/assets/ps5-disc-edition.jpeg'),
    ('PS5 Slim Disc Edition (новая)',        'new',  '/assets/ps5-slim-disc-edition.jpg'),
    ('PS5 Slim Disc Edition (Б/У)',          'used', '/assets/ps5-slim-disc-edition.jpg'),
    ('PS5 Slim Digital Edition (новая)',     'new',  '/assets/ps5-slim-digital-edition.jpg'),
    ('PS5 Slim Digital Edition (Б/У)',       'used', '/assets/ps5-slim-digital-edition.jpg'),
    ('PS4 Slim',                             'used', '/assets/ps4-slim.jpg'),
    ('PS4 Pro',                              'new',  '/assets/ps4-pro.jpg'),
    ('PS4 Pro',                              'used', '/assets/ps4-pro.jpg'),

    ('Ghost of Tsushima (диск)',             'new',  '/assets/ps5-ghost-of-tsushima-disk.jpg'),
    ('The Last of Us Part II (диск)',        'used', '/assets/ps5-the-last-of-us-two.jpg'),
    ('PlayStation-аккаунт (набор игр)',      'new',  '/assets/playstation-account-games.jpg'),
    ('EA Sports FC 25 (диск)',               'used', '/assets/ps5-fc25.jpg'),

    ('iPhone 17 Pro',                        'new',  '/assets/iphone-17-pro.jpg'),
    ('iPhone 15',                            'used', '/assets/iphone-15.jpg'),
    ('Samsung Galaxy S25',                   'used', '/assets/samsung-s25.jpg'),
    ('Samsung Galaxy S25 Ultra',             'new',  '/assets/samsung-s25-ultra.jpg'),

    ('Dyson Airwrap',                        'new',  '/assets/dyson-airwrap.jpg'),
    ('Dyson V15 (пылесос)',                  'used', '/assets/dyson-v15.jpg'),
    ('Dyson Supersonic',                     'new',  '/assets/dyson-supersonic.jpg')
) AS v(name, condition, img)
JOIN products p ON p.name = v.name AND p.condition = v.condition
WHERE NOT EXISTS (
    SELECT 1 FROM product_images pi WHERE pi.product_id = p.id
);

COMMIT;

-- Проверка результата:
-- SELECT c.name AS category, COUNT(p.id) AS products_count
-- FROM categories c LEFT JOIN products p ON p.category_id = c.id
-- GROUP BY c.name ORDER BY c.name;
