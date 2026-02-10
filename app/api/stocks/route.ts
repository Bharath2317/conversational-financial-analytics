import { NextResponse } from "next/server";

interface StockMeta {
  name: string;
  sector: string;
  basePrice: number;
  marketCap: string;
  exchange: "NSE" | "BSE";
}

export const INDIAN_STOCKS: Record<string, StockMeta> = {
  RELIANCE: { name: "Reliance Industries", sector: "Oil & Gas", basePrice: 2945, marketCap: "19.9L Cr", exchange: "NSE" },
  TCS: { name: "Tata Consultancy Services", sector: "IT", basePrice: 4125, marketCap: "14.9L Cr", exchange: "NSE" },
  HDFCBANK: { name: "HDFC Bank", sector: "Banking", basePrice: 1735, marketCap: "13.2L Cr", exchange: "NSE" },
  INFY: { name: "Infosys", sector: "IT", basePrice: 1890, marketCap: "7.8L Cr", exchange: "NSE" },
  ICICIBANK: { name: "ICICI Bank", sector: "Banking", basePrice: 1285, marketCap: "8.9L Cr", exchange: "NSE" },
  HINDUNILVR: { name: "Hindustan Unilever", sector: "FMCG", basePrice: 2520, marketCap: "5.9L Cr", exchange: "NSE" },
  SBIN: { name: "State Bank of India", sector: "Banking", basePrice: 825, marketCap: "7.4L Cr", exchange: "NSE" },
  BHARTIARTL: { name: "Bharti Airtel", sector: "Telecom", basePrice: 1685, marketCap: "10.1L Cr", exchange: "NSE" },
  ITC: { name: "ITC Limited", sector: "FMCG", basePrice: 468, marketCap: "5.8L Cr", exchange: "NSE" },
  KOTAKBANK: { name: "Kotak Mahindra Bank", sector: "Banking", basePrice: 1830, marketCap: "3.6L Cr", exchange: "NSE" },
  LT: { name: "Larsen & Toubro", sector: "Infrastructure", basePrice: 3625, marketCap: "5.0L Cr", exchange: "NSE" },
  AXISBANK: { name: "Axis Bank", sector: "Banking", basePrice: 1175, marketCap: "3.6L Cr", exchange: "NSE" },
  WIPRO: { name: "Wipro", sector: "IT", basePrice: 298, marketCap: "3.1L Cr", exchange: "NSE" },
  HCLTECH: { name: "HCL Technologies", sector: "IT", basePrice: 1820, marketCap: "4.9L Cr", exchange: "NSE" },
  ASIANPAINT: { name: "Asian Paints", sector: "Consumer Goods", basePrice: 2850, marketCap: "2.7L Cr", exchange: "NSE" },
  MARUTI: { name: "Maruti Suzuki", sector: "Automobile", basePrice: 12450, marketCap: "3.9L Cr", exchange: "NSE" },
  SUNPHARMA: { name: "Sun Pharmaceutical", sector: "Pharma", basePrice: 1830, marketCap: "4.4L Cr", exchange: "NSE" },
  TATAMOTORS: { name: "Tata Motors", sector: "Automobile", basePrice: 785, marketCap: "2.9L Cr", exchange: "NSE" },
  BAJFINANCE: { name: "Bajaj Finance", sector: "Financial Services", basePrice: 7250, marketCap: "4.5L Cr", exchange: "NSE" },
  TITAN: { name: "Titan Company", sector: "Consumer Goods", basePrice: 3580, marketCap: "3.2L Cr", exchange: "NSE" },
  NESTLEIND: { name: "Nestle India", sector: "FMCG", basePrice: 2450, marketCap: "2.4L Cr", exchange: "NSE" },
  ULTRACEMCO: { name: "UltraTech Cement", sector: "Cement", basePrice: 11200, marketCap: "3.2L Cr", exchange: "NSE" },
  NTPC: { name: "NTPC Limited", sector: "Power", basePrice: 368, marketCap: "3.6L Cr", exchange: "NSE" },
  POWERGRID: { name: "Power Grid Corp", sector: "Power", basePrice: 325, marketCap: "3.0L Cr", exchange: "NSE" },
  TATASTEEL: { name: "Tata Steel", sector: "Metals", basePrice: 152, marketCap: "1.9L Cr", exchange: "NSE" },
  ONGC: { name: "Oil & Natural Gas Corp", sector: "Oil & Gas", basePrice: 275, marketCap: "3.5L Cr", exchange: "NSE" },
  JSWSTEEL: { name: "JSW Steel", sector: "Metals", basePrice: 985, marketCap: "2.4L Cr", exchange: "NSE" },
  TECHM: { name: "Tech Mahindra", sector: "IT", basePrice: 1690, marketCap: "1.6L Cr", exchange: "NSE" },
  ADANIENT: { name: "Adani Enterprises", sector: "Conglomerate", basePrice: 2890, marketCap: "3.3L Cr", exchange: "NSE" },
  ADANIPORTS: { name: "Adani Ports & SEZ", sector: "Infrastructure", basePrice: 1380, marketCap: "3.0L Cr", exchange: "NSE" },
  BAJAJFINSV: { name: "Bajaj Finserv", sector: "Financial Services", basePrice: 1720, marketCap: "2.7L Cr", exchange: "NSE" },
  COALINDIA: { name: "Coal India", sector: "Mining", basePrice: 485, marketCap: "3.0L Cr", exchange: "NSE" },
  DRREDDY: { name: "Dr. Reddy's Labs", sector: "Pharma", basePrice: 6450, marketCap: "1.1L Cr", exchange: "NSE" },
  CIPLA: { name: "Cipla", sector: "Pharma", basePrice: 1520, marketCap: "1.2L Cr", exchange: "NSE" },
  EICHERMOT: { name: "Eicher Motors", sector: "Automobile", basePrice: 4890, marketCap: "1.3L Cr", exchange: "NSE" },
  GRASIM: { name: "Grasim Industries", sector: "Cement", basePrice: 2680, marketCap: "1.8L Cr", exchange: "NSE" },
  DIVISLAB: { name: "Divi's Laboratories", sector: "Pharma", basePrice: 5920, marketCap: "1.6L Cr", exchange: "NSE" },
  BPCL: { name: "Bharat Petroleum", sector: "Oil & Gas", basePrice: 345, marketCap: "1.5L Cr", exchange: "NSE" },
  HEROMOTOCO: { name: "Hero MotoCorp", sector: "Automobile", basePrice: 5680, marketCap: "1.1L Cr", exchange: "NSE" },
  APOLLOHOSP: { name: "Apollo Hospitals", sector: "Healthcare", basePrice: 6850, marketCap: "1.0L Cr", exchange: "NSE" },
  HDFCLIFE: { name: "HDFC Life Insurance", sector: "Insurance", basePrice: 685, marketCap: "1.5L Cr", exchange: "NSE" },
  SBILIFE: { name: "SBI Life Insurance", sector: "Insurance", basePrice: 1720, marketCap: "1.7L Cr", exchange: "NSE" },
  TATACONSUM: { name: "Tata Consumer Products", sector: "FMCG", basePrice: 1125, marketCap: "1.1L Cr", exchange: "NSE" },
  BRITANNIA: { name: "Britannia Industries", sector: "FMCG", basePrice: 5450, marketCap: "1.3L Cr", exchange: "NSE" },
  INDUSINDBK: { name: "IndusInd Bank", sector: "Banking", basePrice: 1085, marketCap: "84K Cr", exchange: "NSE" },
  HINDALCO: { name: "Hindalco Industries", sector: "Metals", basePrice: 645, marketCap: "1.4L Cr", exchange: "NSE" },
  BAJAJ_AUTO: { name: "Bajaj Auto", sector: "Automobile", basePrice: 9250, marketCap: "2.6L Cr", exchange: "NSE" },
  WIPRO_BSE: { name: "Wipro (BSE)", sector: "IT", basePrice: 298, marketCap: "3.1L Cr", exchange: "BSE" },
  DABUR: { name: "Dabur India", sector: "FMCG", basePrice: 585, marketCap: "1.0L Cr", exchange: "NSE" },
  VEDL: { name: "Vedanta Limited", sector: "Mining", basePrice: 452, marketCap: "1.7L Cr", exchange: "NSE" },
};

const ALL_SYMBOLS = Object.keys(INDIAN_STOCKS);

function generateRealisticPrice(basePrice: number, symbol: string): {
  price: number;
  change: number;
  changePercent: number;
  high: number;
  low: number;
  open: number;
  previousClose: number;
  volume: number;
} {
  const now = Date.now();
  const symbolSeed = symbol.split("").reduce((acc, c) => acc + c.charCodeAt(0), 0);
  const seed = Math.sin((now / 10000) + symbolSeed) * 10000;
  const noise = (Math.sin(seed) + Math.cos(seed * 0.7 + symbolSeed)) / 2;

  const changePercent = noise * 4.5;
  const change = basePrice * (changePercent / 100);
  const price = Number.parseFloat((basePrice + change).toFixed(2));
  const previousClose = basePrice;
  const open = Number.parseFloat((basePrice + change * 0.3).toFixed(2));
  const high = Number.parseFloat((Math.max(price, open) + Math.abs(change * 0.4)).toFixed(2));
  const low = Number.parseFloat((Math.min(price, open) - Math.abs(change * 0.3)).toFixed(2));
  const volume = Math.floor(2000000 + Math.random() * 15000000);

  return {
    price,
    change: Number.parseFloat(change.toFixed(2)),
    changePercent: Number.parseFloat(changePercent.toFixed(2)),
    high,
    low,
    open,
    previousClose,
    volume,
  };
}

export async function GET() {
  const stocks = ALL_SYMBOLS.map((symbol) => {
    const meta = INDIAN_STOCKS[symbol];
    const priceData = generateRealisticPrice(meta.basePrice, symbol);
    return {
      symbol,
      name: meta.name,
      sector: meta.sector,
      marketCap: meta.marketCap,
      exchange: meta.exchange,
      ...priceData,
    };
  });

  return NextResponse.json({ stocks, timestamp: new Date().toISOString() });
}
