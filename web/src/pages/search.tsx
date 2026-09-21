import React, { useState } from "react";
import { Payment, SearchResults } from "../components/SearchResults";

async function fetchPayments(query: string): Promise<Payment[]> {
  const response = await fetch(`/api/payments?q=${encodeURIComponent(query)}`);
  if (!response.ok) {
    throw new Error(`search failed: ${response.status}`);
  }
  const body = await response.json();
  return body.payments;
}

export default function SearchPage() {
  const [query, setQuery] = useState("");
  const [payments, setPayments] = useState<Payment[]>([]);

  return (
    <main>
      <h1>Payments</h1>
      <input
        value={query}
        placeholder="Search by id or reference"
        onChange={(event) => setQuery(event.target.value)}
      />
      <button onClick={() => fetchPayments(query).then(setPayments)}>Search</button>
      <SearchResults payments={payments} />
    </main>
  );
}
