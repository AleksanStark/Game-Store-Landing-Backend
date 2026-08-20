#!/usr/bin/env bash
set -euo pipefail

# ЗАПОЛНИ: реальный адрес твоего фронтенда на Vercel (без слэша в конце)
FRONTEND_URL="https://tim-game-store-landing.vercel.app"

# Папка, куда nginx смотрит через alias /uploads/ -> .../uploads/
# (та же папка, куда image_service.py сохраняет реальные загрузки через форму)
DEST_DIR="uploads/products"

mkdir -p "$DEST_DIR"

FILES=(
  "ps5-pro.jpeg"
  "ps5-digital-edition.jpeg"
  "ps-vr-2.jpeg"
  "ps5-disc-edition.jpeg"
  "ps5-slim-disc-edition.jpg"
  "ps5-slim-digital-edition.jpg"
  "ps4-slim.jpg"
  "ps4-pro.jpg"
  "ps5-ghost-of-tsushima-disk.jpg"
  "ps5-the-last-of-us-two.jpg"
  "playstation-account-games.jpg"
  "ps5-fc25.jpg"
  "iphone-17-pro.jpg"
  "iphone-15.jpg"
  "samsung-s25.jpg"
  "samsung-s25-ultra.jpg"
  "dyson-airwrap.jpg"
  "dyson-v15.jpg"
  "dyson-supersonic.jpg"
)

for file in "${FILES[@]}"; do
  echo "Скачиваю: $file"
  curl -fsSL "$FRONTEND_URL/assets/$file" -o "$DEST_DIR/$file" \
    || echo "  !! не удалось скачать $file — проверь, есть ли он по этому URL"
done

echo ""
echo "Готово. Проверка:"
ls -la "$DEST_DIR"