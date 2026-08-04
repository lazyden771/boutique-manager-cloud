import {
  IonPage, IonHeader, IonToolbar, IonTitle, IonContent, IonList, IonItem, IonLabel,
  IonButton, IonNote,
} from "@ionic/react";
import { useAuth } from "../context/AuthContext";

export default function Settings() {
  const { shopName, currency, logout } = useAuth();

  return (
    <IonPage>
      <IonHeader><IonToolbar><IonTitle>Settings</IonTitle></IonToolbar></IonHeader>
      <IonContent className="ion-padding">
        <IonList>
          <IonItem>
            <IonLabel>Shop Name</IonLabel>
            <IonNote slot="end">{shopName}</IonNote>
          </IonItem>
          <IonItem>
            <IonLabel>Currency</IonLabel>
            <IonNote slot="end">{currency}</IonNote>
          </IonItem>
        </IonList>
        <IonButton expand="block" color="danger" className="ion-margin-top" onClick={logout}>
          Log Out
        </IonButton>
      </IonContent>
    </IonPage>
  );
}
