#!/usr/bin/env python3
"""Юнит-экономика товара на Kaspi.kz.

Использование:
  python unit_economics.py --json '{"sale_price": 8990, "purchase_price": 25, "purchase_currency_rate": 70}'
  python unit_economics.py --file params.json

Все суммы в тенге, кроме purchase_price (в валюте поставщика, пересчитывается по purchase_currency_rate).
Проценты задаются долями: 0.109 = 10,9%.
"""
import argparse
import json
import sys

DEFAULTS = {
    "sale_price": None,               # цена продажи на Kaspi, ₸ (обязательно)
    "purchase_price": None,           # цена закупки за шт. в валюте поставщика (обязательно)
    "purchase_currency_rate": 1.0,    # курс валюты поставщика к тенге (1 для закупки в ₸)
    "weight_kg": 0.0,                 # вес единицы с упаковкой, кг
    "cargo_per_kg": 0.0,              # карго, ₸ за кг
    "china_domestic_per_unit": 0.0,   # доставка по Китаю до склада карго, ₸/шт
    "customs_pct": 0.0,               # растаможка/сборы, доля от закупочной стоимости в ₸
    "packaging": 150.0,               # упаковка/маркировка, ₸/шт
    "commission_pct": 0.125,          # комиссия категории Kaspi С НДС (официальный PDF Kaspi 2026)
    "vat_on_commission": 0.0,         # 0, т.к. commission_pct уже с НДС; ставь 0.16 только если вводишь ставку без НДС
    "red_share": 0.0,                 # доля продаж в рассрочку Red
    "red_fee_pct": 0.0,               # доплата за Red (доля от цены, без НДС)
    "delivery": None,                 # Kaspi Доставка, ₸; None = авто по тарифной сетке Kaspi 2026 (с НДС)
    "delivery_zone": "kz",            # city | kz | express — для авто-расчёта доставки
    "tax_pct": 0.04,                  # налог от выручки
    "ads_pct": 0.0,                   # реклама, доля от цены
    "return_rate": 0.03,              # доля возвратов
    "return_loss_extra": 0.0,         # доп. потери на возврате (уценка), ₸
    "target_margin": 0.25,            # целевая маржа для расчёта макс. закупки
}

WARN_DEFAULTS = ["commission_pct", "delivery_zone", "tax_pct", "return_rate", "packaging"]

# Тарифы Kaspi Доставки 2026, с НДС 16% (от пользователя, сверено с Kaspi Гидом)
# до 10 000 ₸ — по сумме заказа, независимо от веса: (верхняя граница, город, Казахстан, express)
_TIERS_SUM = [(1000, 57, 57, 57), (3000, 173, 173, 173), (5000, 231, 231, 231), (10000, 811, 927, 927)]
# от 10 000 ₸ — по весу: (верхняя граница кг, город, Казахстан, express)
_TIERS_KG = [(5, 1275, 1507, 1971), (15, 1565, 1971, 2145), (30, 2667, 4175, 3653),
             (60, 3363, 6553, 4175), (100, 4813, 9917, 6553), (float("inf"), 7481, 13919, 9802)]


def kaspi_delivery(price, weight_kg, zone="kz"):
    col = {"city": 1, "kz": 2, "express": 3}[zone]
    if price < 10000:
        for row in _TIERS_SUM:
            if price < row[0]:
                return float(row[col])
    for row in _TIERS_KG:
        if weight_kg <= row[0]:
            return float(row[col])


def compute(p):
    price = float(p["sale_price"])
    if p.get("delivery") is None:
        p = {**p, "delivery": kaspi_delivery(price, float(p["weight_kg"]), p["delivery_zone"])}
    purchase_kzt = float(p["purchase_price"]) * float(p["purchase_currency_rate"])
    cargo = float(p["weight_kg"]) * float(p["cargo_per_kg"])
    customs = purchase_kzt * float(p["customs_pct"])
    landed = purchase_kzt + cargo + float(p["china_domestic_per_unit"]) + customs + float(p["packaging"])

    vat_mult = 1 + float(p["vat_on_commission"])
    pct_commission = float(p["commission_pct"]) * vat_mult
    pct_red = float(p["red_share"]) * float(p["red_fee_pct"]) * vat_mult
    pct_total = pct_commission + pct_red + float(p["tax_pct"]) + float(p["ads_pct"])

    returns = float(p["return_rate"]) * (float(p["delivery"]) + float(p["packaging"]) + float(p["return_loss_extra"]))
    fixed = landed + float(p["delivery"]) + returns

    commission = price * pct_commission
    red = price * pct_red
    tax = price * float(p["tax_pct"])
    ads = price * float(p["ads_pct"])
    profit = price - fixed - commission - red - tax - ads
    margin = profit / price if price else 0
    roi = profit / landed if landed else 0

    denom_be = 1 - pct_total
    breakeven = fixed / denom_be if denom_be > 0 else None
    tm = float(p["target_margin"])
    denom_t = 1 - pct_total - tm
    price_for_target = fixed / denom_t if denom_t > 0 else None

    # максимальная себестоимость (landed) для целевой маржи при текущей цене
    max_landed = price * (1 - pct_total - tm) - float(p["delivery"]) - returns
    non_purchase = cargo + float(p["china_domestic_per_unit"]) + float(p["packaging"])
    max_purchase_kzt = (max_landed - non_purchase) / (1 + float(p["customs_pct"]))
    rate = float(p["purchase_currency_rate"])
    max_purchase_supplier = max_purchase_kzt / rate if rate else None

    r = lambda x: None if x is None else round(x, 2)
    return {
        "себестоимость_шт": r(landed),
        "  закупка_в_тенге": r(purchase_kzt),
        "  карго": r(cargo),
        "  растаможка": r(customs),
        "комиссия_kaspi_с_НДС": r(commission),
        "доплата_Red": r(red),
        "доставка_kaspi": r(float(p["delivery"])),
        "налог": r(tax),
        "реклама": r(ads),
        "возвраты_резерв": r(returns),
        "ПРИБЫЛЬ_шт": r(profit),
        "маржа_%": r(margin * 100),
        "ROI_%": r(roi * 100),
        "цена_безубыточности": r(breakeven),
        f"цена_для_маржи_{int(tm*100)}%": r(price_for_target),
        f"макс_закупка_для_маржи_{int(tm*100)}%_в_валюте_поставщика": r(max_purchase_supplier),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", help="параметры в JSON")
    ap.add_argument("--file", help="путь к JSON-файлу с параметрами")
    a = ap.parse_args()
    if a.file:
        user = json.load(open(a.file, encoding="utf-8"))
    elif a.json:
        user = json.loads(a.json)
    else:
        ap.error("нужен --json или --file")

    unknown = set(user) - set(DEFAULTS)
    if unknown:
        print(f"Неизвестные параметры: {sorted(unknown)}", file=sys.stderr)
    p = {**DEFAULTS, **user}
    missing = [k for k in ("sale_price", "purchase_price") if p[k] is None]
    if missing:
        sys.exit(f"Не хватает обязательных параметров: {missing}")

    result = compute(p)
    assumed = [k for k in WARN_DEFAULTS if k not in user]
    out = {"результат": result, "допущения_по_умолчанию": {k: DEFAULTS[k] for k in assumed}}
    print(json.dumps(out, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
