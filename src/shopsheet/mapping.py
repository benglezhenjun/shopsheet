from __future__ import annotations

import pandas as pd

ORDER_COLUMN_ALIASES = {
    "order_id": ["order_id", "order no", "order number", "订单编号", "订单号"],
    "sku": ["sku", "商品编码", "商家编码", "商品sku", "规格编码"],
    "quantity": ["quantity", "qty", "购买数量", "数量", "件数"],
    "unit_price": ["unit_price", "unit price", "成交单价", "单价", "商品单价"],
    "phone": ["phone", "mobile", "收货手机号", "手机号", "联系电话"],
    "shipping_address": ["shipping_address", "address", "收货地址", "地址"],
    "order_date": ["order_date", "order date", "下单时间", "订单时间"],
}

SKU_COLUMN_ALIASES = {
    "sku": ["sku", "商品编码", "商家编码", "商品sku", "规格编码"],
    "product_name": ["product_name", "product name", "商品名称", "品名"],
    "cost": ["cost", "成本价", "成本", "采购价"],
}

REFUND_COLUMN_ALIASES = {
    "refund_id": ["refund_id", "refund no", "退款编号", "退款单号"],
    "order_id": ["order_id", "order no", "order number", "订单编号", "订单号"],
    "refund_amount": ["refund_amount", "refund amount", "退款金额", "退款额"],
    "reason": ["reason", "退款原因", "原因"],
}


def normalize_orders(raw: pd.DataFrame) -> pd.DataFrame:
    normalized = _rename_to_canonical(raw, ORDER_COLUMN_ALIASES)
    required = ["order_id", "sku", "quantity", "unit_price", "phone", "shipping_address"]
    _require_columns(normalized, required, "order")
    cleaned = _coerce_columns(
        normalized,
        ordered_columns=[
            "order_id",
            "sku",
            "quantity",
            "unit_price",
            "phone",
            "shipping_address",
            "order_date",
        ],
        numeric_columns=["quantity", "unit_price"],
        text_columns=["order_id", "sku", "shipping_address", "order_date"],
    )
    cleaned["phone"] = cleaned["phone"].map(_clean_phone_value)
    return cleaned


def normalize_skus(raw: pd.DataFrame) -> pd.DataFrame:
    normalized = _rename_to_canonical(raw, SKU_COLUMN_ALIASES)
    _require_columns(normalized, ["sku", "product_name", "cost"], "SKU")
    return _coerce_columns(
        normalized,
        ordered_columns=["sku", "product_name", "cost"],
        numeric_columns=["cost"],
        text_columns=["sku", "product_name"],
    )


def normalize_refunds(raw: pd.DataFrame) -> pd.DataFrame:
    normalized = _rename_to_canonical(raw, REFUND_COLUMN_ALIASES)
    _require_columns(normalized, ["refund_id", "order_id", "refund_amount"], "refund")
    return _coerce_columns(
        normalized,
        ordered_columns=["refund_id", "order_id", "refund_amount", "reason"],
        numeric_columns=["refund_amount"],
        text_columns=["refund_id", "order_id", "reason"],
    )


def _rename_to_canonical(
    raw: pd.DataFrame, aliases: dict[str, list[str]]
) -> pd.DataFrame:
    normalized_lookup = {
        _normalize_header(alias): canonical
        for canonical, alias_list in aliases.items()
        for alias in alias_list
    }
    rename_map = {
        column: normalized_lookup[_normalize_header(str(column))]
        for column in raw.columns
        if _normalize_header(str(column)) in normalized_lookup
    }
    return raw.rename(columns=rename_map)


def _require_columns(frame: pd.DataFrame, required: list[str], table_name: str) -> None:
    missing = [column for column in required if column not in frame.columns]
    if missing:
        raise ValueError(f"Missing required {table_name} columns: {', '.join(missing)}")


def _coerce_columns(
    frame: pd.DataFrame,
    ordered_columns: list[str],
    numeric_columns: list[str],
    text_columns: list[str],
) -> pd.DataFrame:
    cleaned = frame.copy()
    for column in ordered_columns:
        if column not in cleaned.columns:
            cleaned[column] = ""
    for column in text_columns:
        cleaned[column] = cleaned[column].map(_clean_text_value)
    for column in numeric_columns:
        cleaned[column] = _coerce_numeric_preserving_invalid(cleaned[column])
    return cleaned[ordered_columns]


def _normalize_header(value: str) -> str:
    return value.strip().lower().replace("_", " ")


def _coerce_numeric_preserving_invalid(series: pd.Series) -> pd.Series:
    numeric = pd.to_numeric(series, errors="coerce")
    original_text = series.astype("string").str.strip()
    nonempty = series.notna() & original_text.ne("")
    invalid = numeric.isna() & nonempty
    cleaned = numeric.astype(object)
    cleaned.loc[invalid] = series.loc[invalid]
    cleaned.loc[~nonempty] = 0
    return cleaned


def _clean_text_value(value: object) -> str:
    if pd.isna(value):
        return ""
    return str(value).strip()


def _clean_phone_value(value: object) -> str:
    text = _clean_text_value(value)
    if text.endswith(".0") and text[:-2].isdigit():
        return text[:-2]
    return text
