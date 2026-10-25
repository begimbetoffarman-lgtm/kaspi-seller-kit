# Kaspi seller kit

Набор навыков для Claude Code продавцу на Kaspi.kz: поиск товаров, анализ ниш, поставщики на 1688,
сверка «тот же товар» по фото, юнит-экономика с комиссиями Kaspi.

## Что внутри

| Что | Для чего |
|---|---|
| `skills/tovarka-agents` | команда из пяти ролей: тренды, анализ ниши, закупка, финансист, координатор. Таблица комиссий Kaspi и скрипт юнит-экономики |
| `skills/подбор-поставщика` (`/подбор-поставщика`) | товар с Kaspi → кандидаты на 1688 → сверка по фото → маржа по живому курсу |
| `vault-template/` | база товаров для Obsidian: шаблоны ниши, товара, поставщика, таблица с маржой и ROI |
| `CLAUDE.md` | правила работы (фото до расчёта, живой курс, без выдуманных цифр, ссылки на поставщиков) |
| `install.ps1`, `install.sh` | установщики |
| `INSTALL.md` | пошаговая инструкция для Claude Code |

## Быстрая установка

Откройте Claude Code и вставьте текст из файла `PROMPT.md`. Claude Code скачает репозиторий и
всё установит сам. Руками:

```powershell
git clone https://github.com/begimbetoffarman-lgtm/kaspi-seller-kit $HOME\kaspi-seller-kit
powershell -ExecutionPolicy Bypass -File $HOME\kaspi-seller-kit\install.ps1
```

```bash
git clone https://github.com/begimbetoffarman-lgtm/kaspi-seller-kit ~/kaspi-seller-kit
bash ~/kaspi-seller-kit/install.sh
```

## Что нужно будет сделать самому

1. Войти в 1688 по QR-коду (`1688-cli`).
2. По желанию: подключить Redstat (платный) для данных по продажам Kaspi.
3. По желанию: поставить Obsidian и открыть `~/kaspi-agents`.

## Чего в наборе нет

Ключей, паролей, входов, личных баз товаров и фирменных стилей автора. Ваши ниши и товары вы
наполняете сами.

## Обновление

```bash
git -C ~/kaspi-seller-kit pull
```
затем снова запустить установщик с `-Force` / `--force` (перезапишет навыки и `CLAUDE.md`, ваши ниши и товары не тронет).
