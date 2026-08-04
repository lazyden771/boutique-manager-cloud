import { useEffect, useState } from "react";
import {
  IonPage, IonHeader, IonToolbar, IonTitle, IonContent, IonSearchbar, IonList,
  IonItem, IonLabel, IonButton, IonInput, IonSelect, IonSelectOption, IonToast,
  IonItemDivider, IonBadge, IonModal, IonButtons, IonIcon, IonTextarea,
} from "@ionic/react";
import { close } from "ionicons/icons";
import { api } from "../api/client";
import { useAuth } from "../context/AuthContext";
import type { Product, Customer, Sale } from "../api/types";

export default function Sales() {
  const { currency } = useAuth();
  const [search, setSearch] = useState("");
  const [products, setProducts] = useState<Product[]>([]);
  const [selected, setSelected] = useState<Product | null>(null);
  const [quantity, setQuantity] = useState("1");
  const [discount, setDiscount] = useState("0");
  const [customers, setCustomers] = useState<Customer[]>([]);
  const [customerId, setCustomerId] = useState<number | null>(null);
  const [recentSales, setRecentSales] = useState<Sale[]>([]);
  const [toast, setToast] = useState("");
  const [error, setError] = useState("");
  const [refundTarget, setRefundTarget] = useState<Sale | null>(null);
  const [refundQuantity, setRefundQuantity] = useState("1");
  const [refundReason, setRefundReason] = useState("");
  const [refundError, setRefundError] = useState("");

  async function loadProducts() {
    const res = await api.get("/products", { params: search ? { search } : {} });
    setProducts(res.data);
  }

  async function loadRecentSales() {
    const res = await api.get("/sales", { params: { limit: 10 } });
    setRecentSales(res.data);
  }

  useEffect(() => {
    loadProducts();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [search]);

  useEffect(() => {
    api.get("/customers").then((res) => setCustomers(res.data));
    loadRecentSales();
  }, []);

  async function handleRecordSale() {
    if (!selected) return;
    setError("");
    try {
      await api.post("/sales", {
        product_id: selected.id,
        quantity_sold: parseInt(quantity, 10),
        discount: parseFloat(discount) || 0,
        customer_id: customerId,
      });
      setToast("Sale recorded.");
      setSelected(null);
      setQuantity("1");
      setDiscount("0");
      setCustomerId(null);
      loadProducts();
      loadRecentSales();
    } catch (err: any) {
      setError(err.response?.data?.detail || "Could not record sale.");
    }
  }

  async function handleRefund() {
    if (!refundTarget) return;
    setRefundError("");
    try {
      await api.post("/refunds", {
        sale_id: refundTarget.id,
        quantity_refunded: parseInt(refundQuantity, 10),
        reason: refundReason || null,
      });
      setToast(`${refundQuantity} unit(s) refunded.`);
      setRefundTarget(null);
      loadRecentSales();
      loadProducts();
    } catch (err: any) {
      setRefundError(err.response?.data?.detail || "Could not process refund.");
    }
  }

  function openRefundDialog(sale: Sale) {
    setRefundTarget(sale);
    setRefundQuantity("1");
    setRefundReason("");
    setRefundError("");
  }

  return (
    <IonPage>
      <IonHeader>
        <IonToolbar><IonTitle>Sell Product</IonTitle></IonToolbar>
        <IonToolbar>
          <IonSearchbar
            value={search}
            placeholder="Search products to sell"
            onIonInput={(e) => setSearch(e.detail.value || "")}
          />
        </IonToolbar>
      </IonHeader>
      <IonContent className="ion-padding">
        {!selected && (
          <IonList>
            {products.map((p) => (
              <IonItem key={p.id} button onClick={() => setSelected(p)}>
                <IonLabel>
                  {p.brand} - {p.suit_name}
                  <p>{currency || "PKR"} {p.selling_price} · {p.quantity} in stock</p>
                </IonLabel>
              </IonItem>
            ))}
          </IonList>
        )}

        {selected && (
          <>
            <IonItem>
              <IonLabel>
                <h2>{selected.brand} - {selected.suit_name}</h2>
                <p>{selected.quantity} in stock</p>
              </IonLabel>
              <IonButton fill="clear" onClick={() => setSelected(null)}>Change</IonButton>
            </IonItem>
            <IonItem>
              <IonInput label="Quantity" labelPlacement="stacked" type="number" value={quantity}
                onIonInput={(e) => setQuantity(e.detail.value || "1")} />
            </IonItem>
            <IonItem>
              <IonInput label="Discount" labelPlacement="stacked" type="number" value={discount}
                onIonInput={(e) => setDiscount(e.detail.value || "0")} />
            </IonItem>
            <IonItem>
              <IonSelect label="Customer" labelPlacement="stacked" placeholder="Walk-in"
                value={customerId} onIonChange={(e) => setCustomerId(e.detail.value)}>
                {customers.map((c) => (
                  <IonSelectOption key={c.id} value={c.id}>{c.name}</IonSelectOption>
                ))}
              </IonSelect>
            </IonItem>
            {error && <p style={{ color: "var(--ion-color-danger)" }}>{error}</p>}
            <IonButton expand="block" className="ion-margin-top" onClick={handleRecordSale}>
              Record Sale
            </IonButton>
          </>
        )}

        <IonItemDivider className="ion-margin-top">Recent Transactions</IonItemDivider>
        <IonList>
          {recentSales.map((s) => (
            <IonItem key={s.id}>
              <IonLabel>
                <h3>{currency || "PKR"} {s.total_amount}</h3>
                <p>{s.quantity_sold} unit(s) · {new Date(s.sale_date).toLocaleString()}</p>
              </IonLabel>
              <IonBadge color="success" style={{ marginRight: 8 }}>
                +{currency || "PKR"} {s.profit}
              </IonBadge>
              <IonButton size="small" fill="outline" onClick={() => openRefundDialog(s)}>
                Refund
              </IonButton>
            </IonItem>
          ))}
          {recentSales.length === 0 && (
            <IonItem><IonLabel>No sales recorded yet.</IonLabel></IonItem>
          )}
        </IonList>

        <IonModal isOpen={!!refundTarget} onDidDismiss={() => setRefundTarget(null)}>
          <IonHeader>
            <IonToolbar>
              <IonTitle>Process Refund</IonTitle>
              <IonButtons slot="end">
                <IonButton onClick={() => setRefundTarget(null)}><IonIcon icon={close} /></IonButton>
              </IonButtons>
            </IonToolbar>
          </IonHeader>
          <IonContent className="ion-padding">
            {refundTarget && (
              <>
                <IonItem lines="none">
                  <IonLabel>
                    <h2>{currency || "PKR"} {refundTarget.total_amount} total sale</h2>
                    <p>{refundTarget.quantity_sold} unit(s) originally sold</p>
                  </IonLabel>
                </IonItem>
                <IonItem>
                  <IonInput
                    label="Quantity to refund" labelPlacement="stacked" type="number"
                    value={refundQuantity} onIonInput={(e) => setRefundQuantity(e.detail.value || "1")}
                  />
                </IonItem>
                <IonItem>
                  <IonTextarea
                    label="Reason (optional)" labelPlacement="stacked" value={refundReason}
                    placeholder="e.g. Wrong size, customer changed mind"
                    onIonInput={(e) => setRefundReason(e.detail.value || "")}
                  />
                </IonItem>
                {refundError && <p style={{ color: "var(--ion-color-danger)" }}>{refundError}</p>}
                <IonButton expand="block" color="danger" className="ion-margin-top" onClick={handleRefund}>
                  Process Refund
                </IonButton>
              </>
            )}
          </IonContent>
        </IonModal>

        <IonToast isOpen={!!toast} message={toast} duration={2000} onDidDismiss={() => setToast("")} />
      </IonContent>
    </IonPage>
  );
}
