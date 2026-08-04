import { useState } from "react";
import { useHistory } from "react-router-dom";
import {
  IonPage, IonContent, IonInput, IonButton, IonItem, IonText, IonSpinner, IonNote,
} from "@ionic/react";
import { useAuth } from "../context/AuthContext";

export default function Signup() {
  const { signup } = useAuth();
  const history = useHistory();
  const [shopName, setShopName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      await signup(shopName, email, password);
      history.push("/dashboard");
    } catch (err: any) {
      const detail = err.response?.data?.detail;
      setError(
        typeof detail === "string"
          ? detail
          : "Could not create your shop. Check your details and try again."
      );
    } finally {
      setLoading(false);
    }
  }

  return (
    <IonPage>
      <IonContent fullscreen className="auth-page">
        <div className="auth-hero">
          <div className="auth-hero-stitch" aria-hidden="true" />
          <h1 className="brand-wordmark auth-wordmark">Create Your Shop</h1>
          <p className="auth-tagline">Set up in a minute, run from any device.</p>
        </div>
        <div className="auth-card">
          <form onSubmit={handleSubmit}>
            <IonItem className="auth-input">
              <IonInput
                label="Shop Name" labelPlacement="stacked" value={shopName}
                onIonInput={(e) => setShopName(e.detail.value || "")} required
              />
            </IonItem>
            <IonItem className="auth-input">
              <IonInput
                label="Email" labelPlacement="stacked" type="email" value={email}
                onIonInput={(e) => setEmail(e.detail.value || "")} required
              />
            </IonItem>
            <IonItem className="auth-input">
              <IonInput
                label="Password" labelPlacement="stacked" type="password" value={password}
                onIonInput={(e) => setPassword(e.detail.value || "")} required
              />
              <IonNote slot="helper">At least 8 characters</IonNote>
            </IonItem>
            {error && <IonText color="danger"><p className="auth-error">{error}</p></IonText>}
            <IonButton expand="block" type="submit" className="ion-margin-top" disabled={loading}>
              {loading ? <IonSpinner name="dots" /> : "Create Shop"}
            </IonButton>
          </form>
          <IonButton expand="block" fill="clear" routerLink="/login">
            Already have a shop? Log in
          </IonButton>
        </div>
      </IonContent>
    </IonPage>
  );
}
