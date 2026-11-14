"use client";

import React from "react";

export default function ScrollButton({ targetId, children, className, onCloseMenu }) {
  const scrollToSection = () => {
    const el = document.getElementById(targetId);
    if (el) {
      el.scrollIntoView({ behavior: "smooth" });
    }
    if (onCloseMenu) onCloseMenu();
  };

  return (
    <div className="reveal reveal-left delay-800"> 
      <button className={className} onClick={scrollToSection}>
        {children}
      </button>
    </div>
  );
}
