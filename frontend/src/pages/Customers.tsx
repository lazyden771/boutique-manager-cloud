import { useEffect, useState } from "react";
import {
  IonPage, IonHeader, IonToolbar, IonTitle, IonContent, IonList, IonItem, IonLabel,
  IonFab, IonFabButton, IonIcon, IonModal, IonButton, IonButtons, IonInput,
} from "@ionic/react";
import { add, close } from "ionicons/icons";
import { api } from "../api/client";
import type { Customer } from "../api/types";

export default function Customers() {
  const [customers, setCustomers] = useState<Customer[]>([]);
  const [spent, setSpent] = useState<Record<number, number>>({});
  const [showModal, setShowModal] = useState(false);
  const [name, setName] = useState("");
  const [phone, setPhone] = useState("");

  async function load() {
    const res = await api.get("/customers");
    setCustomers(res.data);
    res.data.forEach((c: Customer) => {
      api.get(`/customers/${c.id}/total-spent`).then((r) =>
        setSpent((prev) => ({ ...prev, [c.id]: r.data.total_spent }))
      );
    });
  }

  useEffect(() => {
    load();
  }, []);

  async function handleAdd() {
    await api.post("/customers", { name, phone: phone || null });
    setName("");
    setPhone("");
    setShowModal(false);
    load();
  }

  return (
    <IonPage>
      <IonHeader><IonToolbar><IonTitle>Customers</IonTitle></IonToolbar></IonHeader>
      <IonContent>
        <IonList>
          {customers.map((c) => (
            <IonItem key={c.id}>
              <IonLabel>
                <h2>{c.name}</h2>
                <p>{c.phone || "No phone number"}</p>
              </IonLabel>
              <IonLabel slot="end">{spent[c.id] !== undefined ? `spent ${spent[c.id]}` : ""}</IonLabel>
            </IonItem>
          ))}
          {customers.length === 0 && (
            <IonItem><IonLabel>No customers yet.</IonLabel></IonItem>
          )}
        </IonList>
        <IonFab vertical="bottom" horizontal="end" slot="fixed">
          <IonFabButton onClick={() => setShowModal(true)}><IonIcon icon={add} /></IonFabButton>
        </IonFab>
        <IonModal isOpen={showModal} onDidDismiss={() => setShowModal(false)}>
          <IonHeader>
            <IonToolbar>
              <IonTitle>Add Customer</IonTitle>
              <IonButtons slot="end">
                <IonButton onClick={() => setShowModal(false)}><IonIcon icon={close} /></IonButton>
              </IonButtons>
            </IonToolbar>
          </IonHeader>
          <IonContent className="ion-padding">
            <IonItem>
              <IonInput label="Name" labelPlacement="stacked" value={name}
                onIonInput={(e) => setName(e.detail.value || "")} />
            </IonItem>
            <IonItem>
              <IonInput label="Phone" labelPlacement="stacked" value={phone}
                onIonInput={(e) => setPhone(e.detail.value || "")} />
            </IonItem>
            <IonButton expand="block" className="ion-margin-top" onClick={handleAdd}>Save</IonButton>
          </IonContent>
        </IonModal>
      </IonContent>
    </IonPage>
  );
}
