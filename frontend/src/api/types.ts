export interface Product {
  id: number;
  brand: string;
  product_code: string | null;
  suit_name: string;
  colour: string | null;
  purchase_price: number;
  selling_price: number;
  quantity: number;
  low_stock_threshold: number | null;
  notes: string | null;
  image_url: string | null;
  supplier_id: number | null;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface Customer {
  id: number;
  name: string;
  phone: string | null;
}

export interface Supplier {
  id: number;
  name: string;
  phone: string | null;
  notes: string | null;
}

export interface Sale {
  id: number;
  product_id: number;
  customer_id: number | null;
  quantity_sold: number;
  unit_price: number;
  unit_cost: number;
  discount: number;
  total_amount: number;
  profit: number;
  sale_date: string;
}

export interface Refund {
  id: number;
  sale_id: number;
  product_id: number;
  quantity_refunded: number;
  refund_amount: number;
  profit_reversed: number;
  reason: string | null;
  refund_date: string;
}
