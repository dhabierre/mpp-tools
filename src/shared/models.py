from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping


@dataclass(frozen=True)
class Capital:
    amount: float
    invested_amount: float
    performance: float
    annualized_performance: float
    gain: float
    last_valuated_at: str
    run_at: str

    @classmethod
    def from_api(
        cls,
        payload: Mapping[str, Any],
        run_at: str
    ) -> Capital:
        return cls(
            amount=payload.get("amount"),
            invested_amount=payload.get("totalInvestAmount"),
            performance=payload.get("performance"),
            annualized_performance=payload.get("annualizedPerformance"),
            gain=payload.get("gain"),
            last_valuated_at=payload.get("lastValuatedAt"),
            run_at=run_at
        )

    @classmethod
    def from_row(
        cls,
        row: Mapping[str, Any]
    ) -> Capital:
        return cls(
            amount=row.get("amount"),
            invested_amount=row.get("invested_amount"),
            performance=row.get("performance"),
            annualized_performance=row.get("annualized_performance"),
            gain=row.get("gain"),
            last_valuated_at=row.get("date"),
            run_at=row.get("run_at")
        )

    def to_db_row(
        self
    ) -> dict[str, Any]:
        return {
            "amount": self.amount,
            "invested_amount": self.invested_amount,
            "performance": self.performance,
            "annualized_performance": self.annualized_performance,
            "gain": self.gain,
            "date": self.last_valuated_at,
            "run_at": self.run_at
        }


@dataclass
class CapitalTrend:
    date: str
    performance: float
    gain: float
    amount: float
    invested_amount: float
    run_at: str

    @classmethod
    def from_api(
        cls,
        payload: Mapping[str, Any],
        run_at: str
    ) -> CapitalTrend:
        return cls(
            date=payload.get("date"),
            performance=payload.get("performance"),
            gain=payload.get("gain"),
            amount=payload.get("amount"),
            invested_amount=payload.get("investedAmount"),
            run_at=run_at
        )

    @classmethod
    def from_row(
        cls,
        row: Mapping[str, Any]
    ) -> CapitalTrend:
        return cls(
            date=row.get("date"),
            performance=row.get("performance"),
            gain=row.get("gain"),
            amount=row.get("amount"),
            invested_amount=row.get("invested_amount"),
            run_at=row.get("run_at"),
        )

    def to_db_row(
        self
    ) -> dict[str, Any]:
        return {
            "date": self.date,
            "performance": self.performance,
            "gain": self.gain,
            "amount": self.amount,
            "invested_amount": self.invested_amount,
            "run_at": self.run_at
        }


@dataclass(frozen=True)
class Product:
    guid: str
    slug: str
    name: str
    isin: str
    risk: float | None
    fee_rate: float | None
    dic_path: str
    run_at: str

    @classmethod
    def from_api(cls, guid: str, payload: Mapping[str, Any], run_at: str) -> Product:
        return cls(
            guid=guid,
            slug=payload.get("slug"),
            name=payload.get("name"),
            isin=payload.get("isin"),
            risk=payload.get("risk"),
            fee_rate=payload.get("providerFeeRate"),
            dic_path=payload.get("kidPath"),
            run_at=run_at
        )

    @classmethod
    def from_row(cls, row: Mapping[str, Any]) -> Product:
        return cls(
            guid=row.get("guid"),
            slug=row.get("slug"),
            name=row.get("name"),
            isin=row.get("isin"),
            risk=row.get("risk"),
            fee_rate=row.get("fee_rate"),
            dic_path=row.get("dic_path"),
            run_at=row.get("run_at")
        )

    def to_db_row(self) -> dict[str, Any]:
        return {
            "guid": self.guid,
            "slug": self.slug,
            "name": self.name,
            "isin": self.isin,
            "risk": self.risk,
            "fee_rate": self.fee_rate,
            "dic_path": self.dic_path,
            "run_at": self.run_at
        }


@dataclass(frozen=True)
class Position:
    guid: str
    slug: str
    name: str
    amount: float
    invested_amount: float
    performance: float
    date: str
    run_at: str

    @classmethod
    def from_api(
        cls,
        payload: Mapping[str, Any],
        run_at: str
    ) -> Position:
        return cls(
            guid=payload.get("product").get("@id").rstrip("/").split("/")[-1],
            slug=payload.get("product").get("slug"),
            name=payload.get("product").get("name"),
            amount=payload.get("amount"),
            invested_amount=payload.get("investedAmount"),
            performance=payload.get("performance"),
            date=payload.get("date")[:10],
            run_at=run_at
        )

    @classmethod
    def from_row(
        cls,
        row: Mapping[str, Any]
    ) -> Position:
        return cls(
            guid=row.get("guid"),
            slug=row.get("slug"),
            name=row.get("name"),
            amount=row.get("amount"),
            invested_amount=row.get("invested_amount"),
            performance=row.get("performance"),
            date=row.get("date"),
            run_at=row.get("run_at")
        )

    def to_db_row(
        self
    ) -> dict[str, Any]:
        return {
            "guid": self.guid,
            "slug": self.slug,
            "name": self.name,
            "amount": self.amount,
            "invested_amount": self.invested_amount,
            "performance": self.performance,
            "date": self.date,
            "run_at": self.run_at
        }


@dataclass
class ProductTrend:
    guid: str
    slug: str
    name: str
    amount: float
    date: str
    run_at: str
    tag: str | None  # html render

    @classmethod
    def from_api(
        cls,
        guid: str,
        slug: str,
        name: str,
        payload: Mapping[str, Any],
        run_at: str
    ) -> ProductTrend:
        return cls(
            guid=guid,
            slug=slug,
            name=name,
            amount=payload.get("amount"),
            date=payload.get("date")[:10],
            run_at=run_at,
            tag=None
        )

    @classmethod
    def from_row(
        cls,
        row: Mapping[str, Any]
    ) -> ProductTrend:
        return cls(
            guid=row.get("guid"),
            slug=row.get("slug"),
            name=row.get("name"),
            amount=row.get("amount"),
            date=row.get("date"),
            run_at=row.get("run_at"),
            tag=None
        )

    def to_db_row(
        self
    ) -> dict[str, Any]:
        return {
            "guid": self.guid,
            "slug": self.slug,
            "name": self.name,
            "amount": self.amount,
            "date": self.date,
            "run_at": self.run_at
        }


@dataclass(frozen=True)
class InvestOrder:
    reference: str
    type: str
    sub_type: str
    amount: float
    processed_at: str
    valuated_at: str
    row_id: str
    row_type: str
    row_amount: float
    row_guid: str
    row_slug: str
    row_name: str
    run_at: str

    @classmethod
    def from_api(
        cls,
        payload: Mapping[str, Any],
        detail: Mapping[str, Any],
        product: Product | None,
        run_at: str
    ) -> InvestOrder:
        row_slug = product.slug if product is not None else "N.C."
        row_name = product.name if product is not None else "N.C."
        row_guid = detail.get("product").get("id")

        return cls(
            reference=payload.get("reference"),
            type=payload.get("type"),
            sub_type=payload.get("subType"),
            amount=payload.get("amountDebited"),
            processed_at=payload.get("processedAt")[:10],
            valuated_at=payload.get("valuatedAt")[:10],
            row_id=row_guid,
            row_type=detail.get("type"),
            row_amount=detail.get("amountDebited"),
            row_guid=row_guid,
            row_slug=row_slug,
            row_name=row_name,
            run_at=run_at
        )

    @classmethod
    def from_row(
        cls,
        row: Mapping[str, Any]
    ) -> InvestOrder:
        return cls(
            reference=row.get("reference"),
            type=row.get("type"),
            sub_type=row.get("sub_type"),
            amount=row.get("amount"),
            processed_at=row.get("processed_at"),
            valuated_at=row.get("valuated_at"),
            row_id=row.get("row_id"),
            row_type=row.get("row_type"),
            row_amount=row.get("row_amount"),
            row_guid=row.get("row_guid"),
            row_slug=row.get("row_slug"),
            row_name=row.get("row_name"),
            run_at=row.get("run_at")
        )

    @property
    def guid(
        self
    ) -> str:
        return self.row_guid

    def to_db_row(
        self
    ) -> dict[str, Any]:
        return {
            "reference": self.reference,
            "type": self.type,
            "sub_type": self.sub_type,
            "amount": self.amount,
            "processed_at": self.processed_at,
            "valuated_at": self.valuated_at,
            "row_id": self.row_id,
            "row_type": self.row_type,
            "row_amount": self.row_amount,
            "row_guid": self.row_guid,
            "row_slug": self.row_slug,
            "row_name": self.row_name,
            "run_at": self.run_at
        }


@dataclass(frozen=True)
class Cursor:
    id: str
    guid: str
    slug: str
    name: str
    page: int
    size: int
    update_at: str

    @classmethod
    def from_row(
        cls,
        row: Mapping[str, Any]
    ) -> Cursor:
        return cls(
            id=row.get("id"),
            guid=row.get("guid"),
            slug=row.get("slug"),
            name=row.get("name"),
            page=row.get("page"),
            size=row.get("size"),
            update_at=row.get("update_at")
        )
