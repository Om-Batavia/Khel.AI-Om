from fastapi import HTTPException


def validate_recent_series_length(sample_size: int) -> None:
    if sample_size < 3:
        raise HTTPException(
            status_code=422,
            detail="At least 3 recent performance records are required for regression trend analysis.",
        )


def safe_divide(numerator: float, denominator: float) -> float:
    if denominator == 0:
        return 0.0
    return numerator / denominator


def round_float(value: float, decimals: int = 3) -> float:
    return round(float(value), decimals)
