"use client";

import { useEffect, useState } from "react";

type Frame = {
  id: number;
  name: string;
  collection: string;
  shape: string;
  color: string;
  price: number;
  tone: string;
  image: string;
  match: number;
};

type CartItem = Frame & { quantity: number };

const frames: Frame[] = [
  { id: 1, name: "The Harper", collection: "Everyday Edit", shape: "Oval", color: "Crystal", price: 149, tone: "crystal", image: "/frames/harper-crystal.png", match: 96 },
  { id: 2, name: "The Camden", collection: "Heritage", shape: "Round", color: "Tortoise", price: 169, tone: "tortoise", image: "/frames/camden-tortoise.png", match: 94 },
  { id: 3, name: "The Monroe", collection: "Modern Line", shape: "Cat-eye", color: "Azure", price: 159, tone: "azure", image: "/frames/monroe-azure.png", match: 91 },
  { id: 4, name: "The Ellis", collection: "Studio", shape: "Square", color: "Ink", price: 179, tone: "ink", image: "/frames/ellis-ink.png", match: 89 },
  { id: 5, name: "The August", collection: "Light Series", shape: "Round", color: "Honey", price: 155, tone: "honey", image: "/frames/august-honey.png", match: 87 },
  { id: 6, name: "The Rowan", collection: "Essential", shape: "Panto", color: "Sage", price: 165, tone: "sage", image: "/frames/rowan-sage.png", match: 85 },
];

const quickActions = [
  { icon: "◎", title: "Scan your face", text: "Get your best fit" },
  { icon: "⇄", title: "Compare frames", text: "View favorites side by side" },
  { icon: "↔", title: "Measure your PD", text: "A guided 2-minute check" },
];

const nearbyStores = [
  { name: "FaceFrame Studio Downtown", distance: "1.2 mi", address: "125 Market Street", pickup: "Ready in 2 hours", delivery: "Same-day delivery" },
  { name: "FaceFrame Optical at Midtown", distance: "2.8 mi", address: "480 Madison Avenue", pickup: "Ready tomorrow", delivery: "Delivery in 1–2 days" },
  { name: "FaceFrame Partner — Vision House", distance: "4.1 mi", address: "72 Riverside Plaza", pickup: "Ready in 4 hours", delivery: "Next-day delivery" },
];

function Glasses({ tone }: { tone: string }) {
  return <div className={`dash-glasses ${tone}`} aria-hidden="true"><span /><i /><span /></div>;
}

function FrameCard({ frame, saved, onSave, onCart }: { frame: Frame; saved: boolean; onSave: () => void; onCart: () => void }) {
  return (
    <article className="frame-card">
      <button className={`save-button ${saved ? "is-saved" : ""}`} type="button" aria-label={saved ? `Remove ${frame.name} from saved frames` : `Save ${frame.name}`} onClick={onSave}>{saved ? "♥" : "♡"}</button>
      <div className="frame-visual"><img src={frame.image} alt={`${frame.name} ${frame.color} ${frame.shape} eyeglasses`} /><span>Virtual try-on</span><b className="ai-match"><i>✦</i> {frame.match}% match</b></div>
      <div className="frame-info">
        <p>{frame.collection}</p>
        <h3>{frame.name}</h3>
        <div className="frame-meta"><span>{frame.shape} · {frame.color}</span><strong>${frame.price}</strong></div>
        <div className="rating"><span>★★★★★</span> 4.8 <small>(283)</small></div>
      </div>
      <button className="add-cart" type="button" onClick={onCart} aria-label={`Add ${frame.name} to cart`}>+</button>
    </article>
  );
}

export default function Dashboard() {
  const [saved, setSaved] = useState<number[]>([2, 4, 5]);
  const [cart, setCart] = useState(0);
  const [notice, setNotice] = useState("Welcome back, Alex");
  const [chatOpen, setChatOpen] = useState(false);
  const [chatInput, setChatInput] = useState("");
  const [storeFinderOpen, setStoreFinderOpen] = useState(false);
  const [storesFound, setStoresFound] = useState(false);
  const [fulfillment, setFulfillment] = useState<"pickup" | "delivery">("pickup");
  const [profileOpen, setProfileOpen] = useState(false);
  const [messages, setMessages] = useState([
    { from: "ai", text: "Hi Alex! I’m your FaceFrame AI stylist. I can help with frame shapes, fit, lenses, or your order." },
  ]);

  useEffect(() => {
    const items: CartItem[] = JSON.parse(localStorage.getItem("faceframe-cart") || "[]");
    setCart(items.reduce((total, item) => total + item.quantity, 0));
  }, []);

  const toggleSaved = (id: number) => setSaved((current) => current.includes(id) ? current.filter((item) => item !== id) : [...current, id]);
  const addToCart = (frame: Frame) => {
    const items: CartItem[] = JSON.parse(localStorage.getItem("faceframe-cart") || "[]");
    const existing = items.find((item) => item.id === frame.id);
    if (existing) existing.quantity += 1;
    else items.push({ ...frame, quantity: 1 });
    localStorage.setItem("faceframe-cart", JSON.stringify(items));
    setCart(items.reduce((total, item) => total + item.quantity, 0));
    setNotice(`${frame.name} added to your cart`);
  };
  const sendChat = () => {
    const question = chatInput.trim();
    if (!question) return;
    const lower = question.toLowerCase();
    let reply = "Based on your fit profile, I’d start with The Camden or The Rowan. Both balance your features while staying lightweight.";
    if (lower.includes("lens") || lower.includes("prescription")) reply = "I can guide you through lens choices. For prescription, billing, or medical questions, I can also bring in a human specialist.";
    if (lower.includes("order") || lower.includes("return") || lower.includes("broken")) reply = "That needs personal attention. I can transfer this conversation to a FaceFrame human support specialist.";
    setMessages((current) => [...current, { from: "user", text: question }, { from: "ai", text: reply }]);
    setChatInput("");
  };
  const requestHuman = () => setMessages((current) => [...current, { from: "ai", text: "I’ve requested a human frame specialist. They’ll join this chat as soon as one is available." }]);

  return (
    <main className="dashboard-shell">
      <div className="dashboard-orb orb-a" /><div className="dashboard-orb orb-b" />
      <header className="dashboard-header">
        <a href="/" className="dashboard-brand" aria-label="FaceFrame home"><img src="/faceframe-logo.jpg" alt="" /><span>FaceFrame<b>.</b></span></a>
        <nav className="dashboard-nav" aria-label="Main navigation">
          <a className="active" href="#discover">Discover</a><a href="#saved">Saved</a><a href="#orders">Orders</a>
        </nav>
        <div className="header-actions">
          <a className="cart-button" href="/cart" aria-label={`Shopping cart with ${cart} items`}><span className="shopping-cart-icon" aria-hidden="true">🛒</span><b>{cart}</b></a>
          <div className="profile-menu-wrap">
            <button className="avatar-button" type="button" aria-label="Open profile menu" aria-haspopup="menu" aria-expanded={profileOpen} onClick={() => setProfileOpen((open) => !open)}>AM</button>
            {profileOpen && (
              <div className="profile-dropdown" role="menu">
                <div className="profile-summary"><span>AM</span><div><strong>Alex Morgan</strong><small>alex.morgan@example.com</small></div></div>
                <div className="profile-membership"><span>FaceFrame member</span><b>Style profile 80% complete</b></div>
                <nav aria-label="Profile actions">
                  <button type="button" role="menuitem" onClick={() => { setNotice("Personal profile selected"); setProfileOpen(false); }}><span>♙</span><div><strong>Personal information</strong><small>Name, email and delivery address</small></div><b>›</b></button>
                  <button type="button" role="menuitem" onClick={() => { setNotice("Account settings selected"); setProfileOpen(false); }}><span>⚙</span><div><strong>Account settings</strong><small>Preferences and notifications</small></div><b>›</b></button>
                  <button type="button" role="menuitem" onClick={() => { setNotice("Privacy & security selected"); setProfileOpen(false); }}><span>◇</span><div><strong>Privacy &amp; security</strong><small>Password and data controls</small></div><b>›</b></button>
                </nav>
                <a className="signout-button" role="menuitem" href="/"><span>↪</span> Sign out</a>
              </div>
            )}
          </div>
        </div>
      </header>

      <div className="dashboard-grid">
        <aside className="dashboard-sidebar">
          <div className="welcome-block"><p>YOUR DASHBOARD</p><h1>Find the pair that feels like you.</h1><span>{notice}</span></div>
          <nav className="side-menu" aria-label="Account tools">
            <button className="selected" type="button"><span>▷</span>Demo video</button>
            <button type="button"><span>◐</span>Lens preferences</button>
            <button type="button"><span>⇄</span>Compare frames</button>
            <button type="button"><span>◇</span>Your insurance</button>
            <button type="button"><span>↔</span>Measure your PD</button>
            <button className="location-menu-button" type="button" onClick={() => setStoreFinderOpen(true)}><span>⌖</span>Nearby stores</button>
          </nav>
        </aside>

        <section className="dashboard-main" id="discover">
          <div className="section-heading"><div><p>START HERE</p><h2>Your perfect fit, simplified.</h2></div><button className="text-button" type="button">View fit profile →</button></div>
          <div className="quick-grid">
            {quickActions.map((action) => <button className="quick-card" type="button" key={action.title}><span>{action.icon}</span><div><strong>{action.title}</strong><small>{action.text}</small></div><b>→</b></button>)}
          </div>

          <div className="section-heading product-heading"><div><p>CURATED FOR YOU</p><h2>Frames picked for your face.</h2></div><button className="text-button" type="button">See all frames →</button></div>
          <div className="product-grid">
            {frames.slice(0, 3).map((frame) => <FrameCard key={frame.id} frame={frame} saved={saved.includes(frame.id)} onSave={() => toggleSaved(frame.id)} onCart={() => addToCart(frame)} />)}
          </div>

          <div className="section-heading product-heading"><div><p>MOST-LOVED</p><h2>Best sellers.</h2></div></div>
          <div className="product-grid">
            {frames.slice(3).map((frame) => <FrameCard key={frame.id} frame={frame} saved={saved.includes(frame.id)} onSave={() => toggleSaved(frame.id)} onCart={() => addToCart(frame)} />)}
          </div>
        </section>

        <aside className="saved-panel" id="saved">
          <div className="saved-heading"><div><p>YOUR SHORTLIST</p><h2>Saved frames</h2></div><span>{saved.length}</span></div>
          <div className="saved-list">
            {saved.length ? frames.filter((frame) => saved.includes(frame.id)).map((frame) => (
              <div className="saved-item" key={frame.id}>
                <img className="saved-frame-image" src={frame.image} alt="" />
                <div><strong>{frame.name}</strong><span>{frame.color} · ${frame.price}</span></div>
                <button type="button" onClick={() => toggleSaved(frame.id)} aria-label={`Remove ${frame.name}`}>×</button>
              </div>
            )) : <p className="empty-state">Save a frame and it will appear here.</p>}
          </div>
          <button className="compare-button" type="button" disabled={saved.length < 2}>Compare {saved.length} frames</button>
          <div className="appointment-card"><span>VIRTUAL STYLING</span><h3>Not sure which one?</h3><p>Book a complimentary 15-minute frame consultation.</p><button type="button">Book a session</button></div>
        </aside>
      </div>

      {storeFinderOpen && (
        <div className="store-modal-backdrop" role="presentation" onMouseDown={() => setStoreFinderOpen(false)}>
          <section className="store-finder" role="dialog" aria-modal="true" aria-labelledby="store-finder-title" onMouseDown={(event) => event.stopPropagation()}>
            <header className="store-finder-header">
              <div><span className="store-kicker">LOCAL SHOPPING</span><h2 id="store-finder-title">Find frames near you.</h2><p>Choose store pickup or delivery from a nearby FaceFrame location.</p></div>
              <button type="button" aria-label="Close store finder" onClick={() => setStoreFinderOpen(false)}>×</button>
            </header>
            <div className="fulfillment-toggle" aria-label="Fulfillment method">
              <button className={fulfillment === "pickup" ? "active" : ""} type="button" onClick={() => setFulfillment("pickup")}><span>⌂</span> Store pickup</button>
              <button className={fulfillment === "delivery" ? "active" : ""} type="button" onClick={() => setFulfillment("delivery")}><span>▣</span> Local delivery</button>
            </div>
            <form className="location-form" onSubmit={(event) => { event.preventDefault(); setStoresFound(true); }}>
              <label className="address-field">Street address<input required type="text" autoComplete="street-address" placeholder="125 Market Street" /></label>
              <label>City<input required type="text" autoComplete="address-level2" placeholder="New York" /></label>
              <label>State<select required defaultValue=""><option value="" disabled>Select state</option><option>New York</option><option>New Jersey</option><option>California</option><option>Texas</option><option>Florida</option><option>Other</option></select></label>
              <label>ZIP / Pincode<input required inputMode="numeric" autoComplete="postal-code" placeholder="10001" /></label>
              <button className="find-store-button" type="submit"><span>⌖</span> Find nearby stores</button>
            </form>
            {storesFound ? (
              <div className="store-results" aria-live="polite">
                <div className="results-heading"><strong>3 nearby locations</strong><span>Sorted by distance</span></div>
                {nearbyStores.map((store, index) => (
                  <article className="store-result" key={store.name}>
                    <div className="map-pin">{index + 1}</div>
                    <div><h3>{store.name}</h3><p>{store.address} · {store.distance}</p><span className="availability-dot" /> <small>{fulfillment === "pickup" ? store.pickup : store.delivery}</small></div>
                    <button type="button" onClick={() => { setNotice(`${fulfillment === "pickup" ? "Pickup" : "Delivery"} selected at ${store.name}`); setStoreFinderOpen(false); }}>{fulfillment === "pickup" ? "Select store" : "Deliver from here"}</button>
                  </article>
                ))}
              </div>
            ) : <div className="store-map-preview"><div className="map-grid" /><span className="preview-pin pin-one">1</span><span className="preview-pin pin-two">2</span><span className="preview-pin pin-three">3</span><p>Enter your location to see live pickup and delivery choices.</p></div>}
          </section>
        </div>
      )}

      <section className={`ai-chat ${chatOpen ? "chat-open" : ""}`} aria-label="FaceFrame AI support">
        {chatOpen && (
          <div className="chat-window">
            <header><div><span className="ai-status" /> <strong>FaceFrame AI Stylist</strong><small>AI help · Human support available</small></div><button type="button" onClick={() => setChatOpen(false)} aria-label="Close chat">×</button></header>
            <div className="chat-messages" aria-live="polite">
              {messages.map((message, index) => <p className={message.from} key={`${message.from}-${index}`}>{message.text}</p>)}
            </div>
            <div className="chat-suggestions"><button type="button" onClick={() => setChatInput("Which frames suit my face?")}>Frame advice</button><button type="button" onClick={() => setChatInput("I need help with my lenses")}>Lens help</button></div>
            <form onSubmit={(event) => { event.preventDefault(); sendChat(); }}><label className="sr-only" htmlFor="chat-question">Ask the FaceFrame AI stylist</label><input id="chat-question" value={chatInput} onChange={(event) => setChatInput(event.target.value)} placeholder="Ask about frames, fit, or orders…" /><button type="submit" aria-label="Send message">→</button></form>
            <button className="human-handoff" type="button" onClick={requestHuman}><span>●</span> Connect with a human specialist</button>
          </div>
        )}
        <button className="chat-launcher" type="button" onClick={() => setChatOpen((open) => !open)} aria-label={chatOpen ? "Close AI support" : "Open AI support"}><span aria-hidden="true">✦</span>{!chatOpen && <b>Need help?</b>}</button>
      </section>
    </main>
  );
}
