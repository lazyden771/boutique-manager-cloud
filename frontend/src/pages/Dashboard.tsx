import { useEffect, useState } from "react";
import {
  IonPage, IonHeader, IonToolbar, IonTitle, IonContent, IonGrid, IonRow, IonCol,
  IonCard, IonCardHeader, IonCardTitle, IonCardContent, IonList, IonItem, IonLabel,
  IonBadge, IonRefresher, IonRefresherContent, type RefresherEventDetail,
} from "@ionic/react";
import { api } from "../api/client";
import { useAuth } from "../context/AuthContext";
import type { Product } from "../api/types";

export default function Dashboard() {
  const { currency } = useAuth();
  const [today, setToday] = useState<{ sales: number; profit: number } | null>(null);
  const [monthProfit, setMonthProfit] = useState<number | null>(null);
  const [inventoryValue, setInventoryValue] = useState<{ inventory_value: number; total_stock: number } | null>(null);
  const [lowStock, setLowStock] = useState<Product[]>([]);

  async function loadAll() {
    const [todayRes, monthRes, invRes, lowStockRes] = await Promise.all([
      api.get("/dashboard/today"),
      api.get("/dashboard/month-profit"),
      api.get("/dashboard/inventory-value"),
      api.get("/products/low-stock"),
    ]);
    setToday(todayRes.data);
    setMonthProfit(monthRes.data.profit);
    setInventoryValue(invRes.data);
    setLowStock(lowStockRes.data);
  }

  useEffect(() => {
    loadAll();
  }, []);

  function handleRefresh(e: CustomEvent<RefresherEventDetail>) {
    loadAll().finally(() => e.detail.complete());
  }

  function money(n: number) {
    return `${currency || "PKR"} ${n.toLocaleString()}`;
  }

  return (
    <IonPage>
      <IonHeader>
        <IonToolbar><IonTitle>Dashboard</IonTitle></IonToolbar>
      </IonHeader>
      <IonContent>
        <IonRefresher slot="fixed" onIonRefresh={handleRefresh}>
          <IonRefresherContent />
        </IonRefresher>
        <IonGrid>
          <IonRow>
            <IonCol size="6">
              <IonCard>
                <IonCardHeader><IonCardTitle>Today's Sales</IonCardTitle></IonCardHeader>
                <IonCardContent className="stat-figure">{today ? money(today.sales) : "..."}</IonCardContent>
              </IonCard>
            </IonCol>
            <IonCol size="6">
              <IonCard>
                <IonCardHeader><IonCardTitle>Today's Profit</IonCardTitle></IonCardHeader>
                <IonCardContent className="stat-figure">{today ? money(today.profit) : "..."}</IonCardContent>
              </IonCard>
            </IonCol>
            <IonCol size="6">
              <IonCard>
                <IonCardHeader><IonCardTitle>Month's Profit</IonCardTitle></IonCardHeader>
                <IonCardContent className="stat-figure">{monthProfit !== null ? money(monthProfit) : "..."}</IonCardContent>
              </IonCard>
            </IonCol>
            <IonCol size="6">
              <IonCard>
                <IonCardHeader><IonCardTitle>Stock Value</IonCardTitle></IonCardHeader>
                <IonCardContent className="stat-figure">
                  {inventoryValue ? money(inventoryValue.inventory_value) : "..."}
                  <div style={{ fontSize: 12, opacity: 0.6, fontFamily: "Manrope, sans-serif", fontWeight: 500 }}>
                    {inventoryValue ? `${inventoryValue.total_stock} units` : ""}
                  </div>
                </IonCardContent>
              </IonCard>
            </IonCol>
          </IonRow>
        </IonGrid>

        <IonCard>
          <IonCardHeader><IonCardTitle>Low Stock</IonCardTitle></IonCardHeader>
          <IonList>
            {lowStock.length === 0 && (
              <IonItem><IonLabel>Nothing low on stock right now.</IonLabel></IonItem>
            )}
            {lowStock.map((p) => (
              <IonItem key={p.id}>
                <IonLabel>
                  {p.brand} - {p.suit_name}
                </IonLabel>
                <IonBadge color="warning">{p.quantity} left</IonBadge>
              </IonItem>
            ))}
          </IonList>
        </IonCard>
      </IonContent>
    </IonPage>
  );
}
