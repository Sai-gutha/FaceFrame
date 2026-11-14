"use client";

import { useEffect, useState } from "react";

type CartItem = { id:number;name:string;collection:string;shape:string;color:string;price:number;image:string;quantity:number };

const sampleItems: CartItem[] = [
  { id:2,name:"The Camden",collection:"Heritage",shape:"Round",color:"Tortoise",price:169,image:"/frames/camden-tortoise.png",quantity:1 },
  { id:4,name:"The Ellis",collection:"Studio",shape:"Square",color:"Ink",price:179,image:"/frames/ellis-ink.png",quantity:1 },
];

export default function CartPage() {
  const [items,setItems]=useState<CartItem[]>([]);
  const [loaded,setLoaded]=useState(false);
  const [fulfillment,setFulfillment]=useState<"delivery"|"pickup">("delivery");

  useEffect(()=>{const stored=localStorage.getItem("faceframe-cart");setItems(stored?JSON.parse(stored):sampleItems);setLoaded(true)},[]);
  const save=(next:CartItem[])=>{setItems(next);localStorage.setItem("faceframe-cart",JSON.stringify(next))};
  const changeQuantity=(id:number,amount:number)=>save(items.map(item=>item.id===id?{...item,quantity:Math.max(1,item.quantity+amount)}:item));
  const remove=(id:number)=>save(items.filter(item=>item.id!==id));
  const subtotal=items.reduce((sum,item)=>sum+item.price*item.quantity,0);
  const delivery=fulfillment==="delivery"&&subtotal>0?12:0;
  const tax=Math.round(subtotal*.08875*100)/100;
  const total=subtotal+delivery+tax;

  return <main className="cart-shell">
    <header className="cart-header"><a href="/dashboard" className="cart-brand"><img src="/faceframe-logo.jpg" alt=""/><span>FaceFrame<b>.</b></span></a><a href="/dashboard" className="back-shopping">← Continue shopping</a></header>
    <section className="cart-hero"><p>YOUR SELECTION</p><h1>Your cart.</h1><span>{items.reduce((sum,item)=>sum+item.quantity,0)} {items.length===1?"item":"items"} reserved for you</span></section>
    <div className="cart-layout">
      <section className="cart-products" aria-label="Shopping cart items">
        {loaded&&items.length===0?<div className="empty-cart"><span>◎</span><h2>Your cart is waiting.</h2><p>Explore AI-matched frames and add a pair you love.</p><a href="/dashboard">Discover frames →</a></div>:items.map(item=><article className="cart-item" key={item.id}>
          <div className="cart-product-image"><img src={item.image} alt={`${item.name} ${item.color} frames`}/><span>✦ AI matched</span></div>
          <div className="cart-product-copy"><p>{item.collection}</p><h2>{item.name}</h2><span>{item.shape} · {item.color}</span><button type="button">Add prescription lenses</button></div>
          <strong className="item-price">${item.price}</strong>
          <div className="quantity-control" aria-label={`Quantity for ${item.name}`}><button type="button" onClick={()=>changeQuantity(item.id,-1)} aria-label="Decrease quantity">−</button><b>{item.quantity}</b><button type="button" onClick={()=>changeQuantity(item.id,1)} aria-label="Increase quantity">+</button></div>
          <strong className="item-total">${item.price*item.quantity}</strong>
          <button className="remove-item" type="button" onClick={()=>remove(item.id)} aria-label={`Remove ${item.name}`}>×</button>
        </article>)}
      </section>
      <aside className="order-summary">
        <div className="summary-heading"><p>ORDER SUMMARY</p><h2>Ready when you are.</h2></div>
        <div className="fulfillment-choice"><button className={fulfillment==="delivery"?"active":""} type="button" onClick={()=>setFulfillment("delivery")}><span>▣</span>Delivery</button><button className={fulfillment==="pickup"?"active":""} type="button" onClick={()=>setFulfillment("pickup")}><span>⌂</span>Store pickup</button></div>
        <div className="summary-lines"><p><span>Subtotal</span><b>${subtotal.toFixed(2)}</b></p><p><span>Estimated tax</span><b>${tax.toFixed(2)}</b></p><p><span>{fulfillment==="delivery"?"Delivery":"Store pickup"}</span><b>{delivery?`$${delivery.toFixed(2)}`:"Free"}</b></p></div>
        <div className="summary-total"><span>Total</span><strong>${total.toFixed(2)}</strong></div>
        <button className="checkout-button" type="button" disabled={!items.length}>Secure checkout <span>→</span></button>
        <p className="secure-note">◇ Secure checkout · Free 30-day returns</p>
        <div className="cart-help"><span>✦</span><div><strong>Need help choosing lenses?</strong><small>Ask the FaceFrame AI stylist before checkout.</small></div></div>
      </aside>
    </div>
  </main>;
}
