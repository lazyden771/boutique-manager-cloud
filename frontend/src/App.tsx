import { Redirect, Route } from "react-router-dom";
import {
  IonApp, IonIcon, IonLabel, IonRouterOutlet, IonTabBar, IonTabButton, IonTabs,
  setupIonicReact,
} from "@ionic/react";
import { IonReactRouter } from "@ionic/react-router";
import {
  home, cube, cart, people, business, settings as settingsIcon,
} from "ionicons/icons";

import { AuthProvider, useAuth } from "./context/AuthContext";
import Login from "./pages/Login";
import Signup from "./pages/Signup";
import Dashboard from "./pages/Dashboard";
import Inventory from "./pages/Inventory";
import Sales from "./pages/Sales";
import Customers from "./pages/Customers";
import Suppliers from "./pages/Suppliers";
import Settings from "./pages/Settings";

/* Core Ionic CSS */
import "@ionic/react/css/core.css";
import "@ionic/react/css/normalize.css";
import "@ionic/react/css/structure.css";
import "@ionic/react/css/typography.css";
import "@ionic/react/css/padding.css";
import "@ionic/react/css/float-elements.css";
import "@ionic/react/css/text-alignment.css";
import "@ionic/react/css/text-transformation.css";
import "@ionic/react/css/flex-utils.css";
import "@ionic/react/css/display.css";

setupIonicReact();

function AuthenticatedTabs() {
  return (
    <IonTabs>
      <IonRouterOutlet>
        <Route exact path="/dashboard" component={Dashboard} />
        <Route exact path="/inventory" component={Inventory} />
        <Route exact path="/sales" component={Sales} />
        <Route exact path="/customers" component={Customers} />
        <Route exact path="/suppliers" component={Suppliers} />
        <Route exact path="/settings" component={Settings} />
        <Route exact path="/">
          <Redirect to="/dashboard" />
        </Route>
      </IonRouterOutlet>
      <IonTabBar slot="bottom">
        <IonTabButton tab="dashboard" href="/dashboard">
          <IonIcon icon={home} />
          <IonLabel>Dashboard</IonLabel>
        </IonTabButton>
        <IonTabButton tab="inventory" href="/inventory">
          <IonIcon icon={cube} />
          <IonLabel>Inventory</IonLabel>
        </IonTabButton>
        <IonTabButton tab="sales" href="/sales">
          <IonIcon icon={cart} />
          <IonLabel>Sell</IonLabel>
        </IonTabButton>
        <IonTabButton tab="customers" href="/customers">
          <IonIcon icon={people} />
          <IonLabel>Customers</IonLabel>
        </IonTabButton>
        <IonTabButton tab="suppliers" href="/suppliers">
          <IonIcon icon={business} />
          <IonLabel>Suppliers</IonLabel>
        </IonTabButton>
        <IonTabButton tab="settings" href="/settings">
          <IonIcon icon={settingsIcon} />
          <IonLabel>Settings</IonLabel>
        </IonTabButton>
      </IonTabBar>
    </IonTabs>
  );
}

function AppRoutes() {
  const { isAuthenticated } = useAuth();

  if (!isAuthenticated) {
    return (
      <IonRouterOutlet>
        <Route exact path="/login" component={Login} />
        <Route exact path="/signup" component={Signup} />
        <Route path="/">
          <Redirect to="/login" />
        </Route>
      </IonRouterOutlet>
    );
  }

  return (
    <IonRouterOutlet>
      <Route path="/" component={AuthenticatedTabs} />
    </IonRouterOutlet>
  );
}

export default function App() {
  return (
    <IonApp>
      <AuthProvider>
        <IonReactRouter>
          <AppRoutes />
        </IonReactRouter>
      </AuthProvider>
    </IonApp>
  );
}
