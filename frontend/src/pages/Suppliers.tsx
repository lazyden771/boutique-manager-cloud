import { useEffect, useState } from "react";
import {
  IonPage, IonHeader, IonToolbar, IonTitle, IonContent, IonList, IonItem, IonLabel,
  IonFab, IonFabButton, IonIcon, IonModal, IonButton, IonButtons, IonInput,
} from "@ionic/react";
import { add, close } from "ionicons/icons";
import { api } from "../api/client";
import type { Supplier } from "../api/types";

export default function Suppliers() {
  const [suppliers, setSuppliers] = useState<Supplier[]>([]);
  const [showModal, setShowModal] = useState(false);
  const [name, setName] = useState("");
  const [phone, setPhone] = useState("");

  async function load() {
    const res = await api.get("/suppliers");
    setSuppliers(res.data);
  }

  useEffect(() => {
    load();
  }, []);

  async function handleAdd() {
    await api.post("/suppliers", { name, phone: phone || null });
    setName("");
    setPhone("");
    setShowModal(false);
    load();
  }

  return (
    <IonPage>
      <IonHeader><IonToolbar><IonTitle>Suppliers</IonTitle></IonToolbar></IonHeader>
      <IonContent>
        <IonList>
          {suppliers.map((s) => (
            <IonItem key={s.id}>
              <IonLabel>
                <h2>{s.name}</h2>
                <p>{s.phone || "No phone number"}</p>
              </IonLabel>
            </IonItem>
          ))}
          {suppliers.length === 0 && (
            <IonItem><IonLabel>No suppliers yet.</IonLabel></IonItem>
          )}
        </IonList>
        <IonFab vertical="bottom" horizontal="end" slot="fixed">
          <IonFabButton onClick={() => setShowModal(true)}><IonIcon icon={add} /></IonFabButton>
        </IonFab>
        <IonModal isOpen={showModal} onDidDismiss={() => setShowModal(false)}>
          <IonHeader>
            <IonToolbar>
              <IonTitle>Add Supplier</IonTitle>
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
