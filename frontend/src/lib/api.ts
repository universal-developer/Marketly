export async function getStock(symbol: string) {
    const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/financials/${symbol}`, {
        cache: "no-store"
    });
    return res.json();
}
