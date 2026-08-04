import { useEffect, useRef, useState } from "react";
import {
  IonPage, IonHeader, IonToolbar, IonTitle, IonContent, IonSearchbar, IonList,
  IonItem, IonLabel, IonBadge, IonFab, IonFabButton, IonIcon, IonModal, IonButton,
  IonButtons, IonInput, IonItemDivider, IonAlert, IonToast, IonThumbnail, IonSpinner,
  IonAvatar,
} from "@ionic/react";
import { add, close, camera } from "ionicons/icons";
import { api } from "../api/client";
import { useAuth } from "../context/AuthContext";
import type { Product } from "../api/types";

const emptyForm = {
  brand: "", suit_name: "", colour: "", product_code: "",
  purchase_price: "", selling_price: "", quantity: "",
};

export default function Inventory() {
  const { currency } = useAuth();
  const [products, setProducts] = useState<Product[]>([]);
  const [search, setSearch] = useState("");
  const [showAddModal, setShowAddModal] = useState(false);
  const [form, setForm] = useState(emptyForm);
  const [error, setError] = useState("");
  const [duplicateAlert, setDuplicateAlert] = useState<{ show: boolean; existingId: number | null }>({
    show: false, existingId: null,
  });
  const [toast, setToast] = useState("");

  // Edit / photo upload state
  const [editingProduct, setEditingProduct] = useState<Product | null>(null);
  const [editForm, setEditForm] = useState(emptyForm);
  const [editError, setEditError] = useState("");
  const [uploading, setUploading] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  async function loadProducts() {
    const res = await api.get("/products", { params: search ? { search } : {} });
    setProducts(res.data);
  }

  useEffect(() => {
    loadProducts();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [search]);

  function resetForm() {
    setForm(emptyForm);
    setError("");
  }

  async function handleAddProduct() {
    setError("");
    try {
      await api.post("/products", {
        brand: form.brand,
        suit_name: form.suit_name,
        colour: form.colour || null,
        product_code: form.product_code || null,
        purchase_price: parseFloat(form.purchase_price),
        selling_price: parseFloat(form.selling_price),
        quantity: parseInt(form.quantity, 10),
      });
      setShowAddModal(false);
      resetForm();
      setToast("Product added.");
      loadProducts();
    } catch (err: any) {
      if (err.response?.status === 409) {
        setDuplicateAlert({ show: true, existingId: err.response.data.detail.existing_product_id });
      } else {
        setError(err.response?.data?.detail || "Could not add product.");
      }
    }
  }

  async function handleIncreaseExisting() {
    if (!duplicateAlert.existingId) return;
    await api.post(`/products/${duplicateAlert.existingId}/increase-quantity`, null, {
      params: { additional_quantity: parseInt(form.quantity, 10) },
    });
    setDuplicateAlert({ show: false, existingId: null });
    setShowAddModal(false);
    resetForm();
    setToast("Existing stock quantity increased.");
    loadProducts();
  }

  function openEditModal(product: Product) {
    setEditingProduct(product);
    setEditForm({
      brand: product.brand,
      suit_name: product.suit_name,
      colour: product.colour || "",
      product_code: product.product_code || "",
      purchase_price: String(product.purchase_price),
      selling_price: String(product.selling_price),
      quantity: String(product.quantity),
    });
    setEditError("");
  }

  async function handleSaveEdit() {
    if (!editingProduct) return;
    setEditError("");
    try {
      await api.put(`/products/${editingProduct.id}`, {
        brand: editForm.brand,
        suit_name: editForm.suit_name,
        colour: editForm.colour || null,
        product_code: editForm.product_code || null,
        purchase_price: parseFloat(editForm.purchase_price),
        selling_price: parseFloat(editForm.selling_price),
        quantity: parseInt(editForm.quantity, 10),
        supplier_id: editingProduct.supplier_id,
      });
      setToast("Product updated.");
      setEditingProduct(null);
      loadProducts();
    } catch (err: any) {
      setEditError(err.response?.data?.detail || "Could not save changes.");
    }
  }

  async function handleDeactivate() {
    if (!editingProduct) return;
    await api.delete(`/products/${editingProduct.id}`);
    setToast("Product removed from inventory.");
    setEditingProduct(null);
    loadProducts();
  }

  function triggerPhotoPicker() {
    fileInputRef.current?.click();
  }

  async function handlePhotoSelected(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (!file || !editingProduct) return;

    setUploading(true);
    setEditError("");
    try {
      const formData = new FormData();
      formData.append("file", file);
      const res = await api.post(`/products/${editingProduct.id}/image`, formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      setEditingProduct(res.data);
      setToast("Photo uploaded.");
      loadProducts();
    } catch (err: any) {
      setEditError(err.response?.data?.detail || "Could not upload photo.");
    } finally {
      setUploading(false);
      if (fileInputRef.current) fileInputRef.current.value = "";
    }
  }

  return (
    <IonPage>
      <IonHeader>
        <IonToolbar><IonTitle>Inventory</IonTitle></IonToolbar>
        <IonToolbar>
          <IonSearchbar value={search} onIonInput={(e) => setSearch(e.detail.value || "")} />
        </IonToolbar>
      </IonHeader>
      <IonContent>
        <IonList>
          {products.map((p) => (
            <IonItem key={p.id} button onClick={() => openEditModal(p)}>
              {p.image_url ? (
                <IonThumbnail slot="start">
                  <img src={p.image_url} alt={p.suit_name} />
                </IonThumbnail>
              ) : (
                <IonAvatar slot="start">
                  <div style={{
                    width: "100%", height: "100%", background: "var(--ion-color-light)",
                    display: "flex", alignItems: "center", justifyContent: "center",
                  }}>
                    <IonIcon icon={camera} color="medium" />
                  </div>
                </IonAvatar>
              )}
              <IonLabel>
                <h2>{p.brand} - {p.suit_name}</h2>
                <p>{p.colour || "No colour set"} · {currency || "PKR"} {p.selling_price}</p>
              </IonLabel>
              <IonBadge color={p.quantity <= (p.low_stock_threshold ?? 5) ? "warning" : "medium"}>
                {p.quantity} in stock
              </IonBadge>
            </IonItem>
          ))}
          {products.length === 0 && (
            <IonItem><IonLabel>No products yet. Tap + to add your first item.</IonLabel></IonItem>
          )}
        </IonList>

        <IonFab vertical="bottom" horizontal="end" slot="fixed">
          <IonFabButton onClick={() => setShowAddModal(true)}>
            <IonIcon icon={add} />
          </IonFabButton>
        </IonFab>

        {/* ---- Add product modal ---- */}
        <IonModal isOpen={showAddModal} onDidDismiss={() => setShowAddModal(false)}>
          <IonHeader>
            <IonToolbar>
              <IonTitle>Add New Stock</IonTitle>
              <IonButtons slot="end">
                <IonButton onClick={() => setShowAddModal(false)}><IonIcon icon={close} /></IonButton>
              </IonButtons>
            </IonToolbar>
          </IonHeader>
          <IonContent className="ion-padding">
            <IonItemDivider>Required</IonItemDivider>
            <IonItem>
              <IonInput label="Brand" labelPlacement="stacked" value={form.brand}
                onIonInput={(e) => setForm({ ...form, brand: e.detail.value || "" })} />
            </IonItem>
            <IonItem>
              <IonInput label="Suit Name" labelPlacement="stacked" value={form.suit_name}
                onIonInput={(e) => setForm({ ...form, suit_name: e.detail.value || "" })} />
            </IonItem>
            <IonItem>
              <IonInput label="Purchase Price" labelPlacement="stacked" type="number" value={form.purchase_price}
                onIonInput={(e) => setForm({ ...form, purchase_price: e.detail.value || "" })} />
            </IonItem>
            <IonItem>
              <IonInput label="Selling Price" labelPlacement="stacked" type="number" value={form.selling_price}
                onIonInput={(e) => setForm({ ...form, selling_price: e.detail.value || "" })} />
            </IonItem>
            <IonItem>
              <IonInput label="Quantity" labelPlacement="stacked" type="number" value={form.quantity}
                onIonInput={(e) => setForm({ ...form, quantity: e.detail.value || "" })} />
            </IonItem>

            <IonItemDivider>Optional</IonItemDivider>
            <IonItem>
              <IonInput label="Colour" labelPlacement="stacked" value={form.colour}
                onIonInput={(e) => setForm({ ...form, colour: e.detail.value || "" })} />
            </IonItem>
            <IonItem>
              <IonInput label="Product Code" labelPlacement="stacked" value={form.product_code}
                onIonInput={(e) => setForm({ ...form, product_code: e.detail.value || "" })} />
            </IonItem>

            {error && <p style={{ color: "var(--ion-color-danger)" }}>{error}</p>}
            <IonButton expand="block" className="ion-margin-top" onClick={handleAddProduct}>
              Save
            </IonButton>
          </IonContent>
        </IonModal>

        {/* ---- Edit product + photo modal ---- */}
        <IonModal isOpen={!!editingProduct} onDidDismiss={() => setEditingProduct(null)}>
          <IonHeader>
            <IonToolbar>
              <IonTitle>Edit Product</IonTitle>
              <IonButtons slot="end">
                <IonButton onClick={() => setEditingProduct(null)}><IonIcon icon={close} /></IonButton>
              </IonButtons>
            </IonToolbar>
          </IonHeader>
          <IonContent className="ion-padding">
            {editingProduct && (
              <>
                <div style={{ display: "flex", justifyContent: "center", marginBottom: 16 }}>
                  <div
                    onClick={triggerPhotoPicker}
                    style={{
                      width: 120, height: 120, borderRadius: 12, overflow: "hidden",
                      background: "var(--ion-color-light)", display: "flex",
                      alignItems: "center", justifyContent: "center", cursor: "pointer",
                    }}
                  >
                    {uploading ? (
                      <IonSpinner />
                    ) : editingProduct.image_url ? (
                      <img src={editingProduct.image_url} alt="" style={{ width: "100%", height: "100%", objectFit: "cover" }} />
                    ) : (
                      <IonIcon icon={camera} size="large" color="medium" />
                    )}
                  </div>
                  <input
                    ref={fileInputRef} type="file" accept="image/jpeg,image/png,image/webp"
                    style={{ display: "none" }} onChange={handlePhotoSelected}
                  />
                </div>
                <p style={{ textAlign: "center", fontSize: 12, opacity: 0.6, marginTop: -8 }}>
                  Tap photo to {editingProduct.image_url ? "change" : "add"}
                </p>

                <IonItemDivider>Details</IonItemDivider>
                <IonItem>
                  <IonInput label="Brand" labelPlacement="stacked" value={editForm.brand}
                    onIonInput={(e) => setEditForm({ ...editForm, brand: e.detail.value || "" })} />
                </IonItem>
                <IonItem>
                  <IonInput label="Suit Name" labelPlacement="stacked" value={editForm.suit_name}
                    onIonInput={(e) => setEditForm({ ...editForm, suit_name: e.detail.value || "" })} />
                </IonItem>
                <IonItem>
                  <IonInput label="Purchase Price" labelPlacement="stacked" type="number" value={editForm.purchase_price}
                    onIonInput={(e) => setEditForm({ ...editForm, purchase_price: e.detail.value || "" })} />
                </IonItem>
                <IonItem>
                  <IonInput label="Selling Price" labelPlacement="stacked" type="number" value={editForm.selling_price}
                    onIonInput={(e) => setEditForm({ ...editForm, selling_price: e.detail.value || "" })} />
                </IonItem>
                <IonItem>
                  <IonInput label="Quantity" labelPlacement="stacked" type="number" value={editForm.quantity}
                    onIonInput={(e) => setEditForm({ ...editForm, quantity: e.detail.value || "" })} />
                </IonItem>
                <IonItem>
                  <IonInput label="Colour" labelPlacement="stacked" value={editForm.colour}
                    onIonInput={(e) => setEditForm({ ...editForm, colour: e.detail.value || "" })} />
                </IonItem>
                <IonItem>
                  <IonInput label="Product Code" labelPlacement="stacked" value={editForm.product_code}
                    onIonInput={(e) => setEditForm({ ...editForm, product_code: e.detail.value || "" })} />
                </IonItem>

                {editError && <p style={{ color: "var(--ion-color-danger)" }}>{editError}</p>}
                <IonButton expand="block" className="ion-margin-top" onClick={handleSaveEdit}>
                  Save Changes
                </IonButton>
                <IonButton expand="block" fill="outline" color="danger" onClick={handleDeactivate}>
                  Remove from Inventory
                </IonButton>
              </>
            )}
          </IonContent>
        </IonModal>

        <IonAlert
          isOpen={duplicateAlert.show}
          header="Matching product found"
          message="A product with this brand, name, and colour already exists. Increase its quantity instead?"
          buttons={[
            { text: "Cancel", role: "cancel", handler: () => setDuplicateAlert({ show: false, existingId: null }) },
            { text: "Increase Quantity", handler: handleIncreaseExisting },
          ]}
        />

        <IonToast isOpen={!!toast} message={toast} duration={2000} onDidDismiss={() => setToast("")} />
      </IonContent>
    </IonPage>
  );
}
