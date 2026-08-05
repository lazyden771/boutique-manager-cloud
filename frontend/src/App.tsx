import { Redirect, Route, Switch, useLocation, useHistory } from "react-router-dom";
import {
  IonApp, IonIcon, IonLabel, IonTabBar, IonTabButton,
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

/* Boutique Manager theme */
import "./theme/variables.css";
import "./theme/global.css";

setupIonicReact();

/*
 * NOTE: This app intentionally avoids <IonRouterOutlet> and <IonTabs>.
 * On the currently pinned versions (@ionic/react-router 8.8.16 with
 * react-router-dom 5.3.4), IonRouterOutlet fails to insert any matched
 * route into its shadow DOM (confirmed on both React 18 and React 19).
 * Plain react-router-dom <Switch>/<Route> renders correctly.
 * Do not revert to IonRouterOutlet/IonTabs unless a future version is confirmed fixed.
 */

const TABS = [
  { tab: "dashboard", href: "/dashboard", icon: home, label: "Dashboard", Page: Dashboard },
  { tab: "inventory", href: "/inventory", icon: cube, label: "Inventory", Page: Inventory },
  { tab: "sales", href: "/sales", icon: cart, label: "Sell", Page: Sales },
  { tab: "customers", href: "/customers", icon: people, label: "Customers", Page: Customers },
  { tab: "suppliers", href: "/suppliers", icon: business, label: "Suppliers", Page: Suppliers },
  { tab: "settings", href: "/settings", icon: settingsIcon, label: "Settings", Page: Settings },
];

function AuthenticatedTabs() {
  const location = useLocation();
  const history = useHistory();
  const activeTab = TABS.find((t) => location.pathname.startsWith(t.href))?.tab ?? "dashboard";

  return (
    <div style={{ display: "flex", flexDirection: "column", height: "100vh", overflow: "hidden" }}>
      {/* Page content fills available space; pages handle their own IonContent scroll */}
      <div style={{ flex: 1, overflow: "hidden", position: "relative" }}>
        <Switch>
          {TABS.map(({ href, Page }) => (
            <Route key={href} exact path={href} component={Page} />
          ))}
          <Route exact path="/">
            <Redirect to="/dashboard" />
          </Route>
        </Switch>
      </div>
      {/* Floating glass tab bar — sits below content, never overlaps it */}
      <IonTabBar slot="bottom" selectedTab={activeTab}>
        {TABS.map(({ tab, href, icon, label }) => (
          <IonTabButton
            key={tab}
            tab={tab}
            selected={activeTab === tab}
            onClick={() => history.push(href)}
          >
            <IonIcon icon={icon} />
            <IonLabel>{label}</IonLabel>
          </IonTabButton>
        ))}
      </IonTabBar>
    </div>
  );
}

function AppRoutes() {
  const { isAuthenticated } = useAuth();

  if (!isAuthenticated) {
    return (
      <Switch>
        <Route exact path="/login" component={Login} />
        <Route exact path="/signup" component={Signup} />
        <Route path="/">
          <Redirect to="/login" />
        </Route>
      </Switch>
    );
  }

  return (
    <Switch>
      <Route path="/" component={AuthenticatedTabs} />
    </Switch>
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
