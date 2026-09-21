import React from "react";

export interface Payment {
  id: string;
  amountMinor: number;
  currency: string;
  status: "pending" | "settled" | "failed";
}

export function formatAmount(amountMinor: number, currency: string): string {
  return `${(amountMinor / 100).toFixed(2)} ${currency}`;
}

export function SearchResults({ payments }: { payments: Payment[] }) {
  if (payments.length === 0) {
    return (
      <div className="empty">
        <p>No payments matched your search.</p>
        <p className="empty__hint">
          Try a payment id, a reference, or widen the date range.
        </p>
      </div>
    );
  }
  return (
    <ul className="results">
      {payments.map((payment, index) => (
        <li
          key={payment.id}
          className={`result result--${payment.status}`}
          aria-rowindex={index + 1}
        >
          <span className="result__id">{payment.id}</span>
          <span className="result__amount">
            {formatAmount(payment.amountMinor, payment.currency)}
          </span>
          <span className="result__status">{payment.status}</span>
        </li>
      ))}
    </ul>
  );
}
