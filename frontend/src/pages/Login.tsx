import { useState } from "react";
import { useHistory } from "react-router-dom";
import {
  IonPage, IonContent, IonInput, IonButton, IonItem, IonText, IonSpinner,
} from "@ionic/react";
import { useAuth } from "../context/AuthContext";

export default function Login() {
  const { login } = useAuth();
  const history = useHistory();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      await login(email, password);
      history.push("/dashboard");
    } catch (err: any) {
      setError(err.response?.data?.detail || "Could not log in. Check your details and try again.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <IonPage>
      <IonContent className="ion-padding">
        <div style={{ maxWidth: 400, margin: "80px auto" }}>
          <h1 style={{ textAlign: "center" }}>Boutique Manager</h1>
          <form onSubmit={handleSubmit}>
            <IonItem>
              <IonInput
                label="Email" labelPlacement="stacked" type="email" value={email}
                onIonInput={(e) => setEmail(e.detail.value || "")} required
              />
            </IonItem>
            <IonItem>
              <IonInput
                label="Password" labelPlacement="stacked" type="password" value={password}
                onIonInput={(e) => setPassword(e.detail.value || "")} required
              />
            </IonItem>
            {error && <IonText color="danger"><p>{error}</p></IonText>}
            <IonButton expand="block" type="submit" className="ion-margin-top" disabled={loading}>
              {loading ? <IonSpinner name="dots" /> : "Log In"}
            </IonButton>
          </form>
          <IonButton expand="block" fill="clear" routerLink="/signup">
            New shop? Sign up
          </IonButton>
        </div>
      </IonContent>
    </IonPage>
  );
}
