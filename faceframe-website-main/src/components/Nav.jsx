"use client";

import React, { useState } from 'react';
import Image from 'next/image';
import { Menu, X } from 'lucide-react';

const Nav = () => {
  const [menuOpen, setMenuOpen] = useState(false);

  const toggleMenu = () => setMenuOpen(!menuOpen);
  const closeMenu = () => setMenuOpen(false);

  const scrollToSection = (id) => {
    const el = document.getElementById(id);
    if (el) {
      el.scrollIntoView({ behavior: 'smooth' });
    }
    closeMenu();
  };

  return (
    <nav className="w-full py-3 bg-white shadow-xs md:bg-inherit md:shadow-none relative z-50">
      <div className="flex items-center justify-between py-2 md:py-4 md:px-10 px-7">
        {/* Logo */}
        <a href="/">
          <div className="w-[180px] md:w-[200px] lg:w-[240px]">
            <Image
              src="/images/faceframe_logo.png"
              alt="FaceFrame Logo"
              width={240}
              height={80}
              priority
              style={{ height: 'auto', width: '100%' }}
            />
          </div>
        </a>

        {/* Desktop nav + mobile toggle */}
        <div className="flex items-center gap-6">
          {/* Desktop Navigation */}
          <ul className="hidden md:flex md:items-center gap-6">
            <li className="nav-item">
              <button
                onClick={() => scrollToSection('features-section')}
                className="cursor-pointer"
              >
                Features
              </button>
            </li>
            <li className="nav-item">
              <button
                onClick={() => scrollToSection('how-it-works-section')}
                className="cursor-pointer"
              >
                How It Works
              </button>
            </li>
            <li className="nav-item">
              <button
                onClick={() => scrollToSection('contact-section')}
                className="primary-btn !px-8 !py-0"
              >
                Contact Us
              </button>
            </li>
          </ul>

          {/* Mobile Menu Toggle */}
          <button
            className="md:hidden text-black z-50"
            onClick={toggleMenu}
            aria-label="Toggle Menu"
          >
            {menuOpen ? <X size={28} /> : <Menu size={28} />}
          </button>
        </div>
      </div>

      {/* Mobile Dropdown Menu */}
      <ul
  className={`
    md:hidden bg-white w-full transform origin-top
    transition-all duration-300 ease-in-out
    overflow-hidden
    ${menuOpen ? 'scale-y-100 opacity-100' : 'scale-y-0 opacity-0 h-0'}
  `}
>


        <li className="nav-item px-6 py-2">
          <button
            onClick={() => scrollToSection('features-section')}
            className="nav-link-button w-full text-left"
          >
            Features
          </button>
        </li>
        <li className="nav-item px-6 py-2">
          <button
            onClick={() => scrollToSection('how-it-works-section')}
            className="nav-link-button w-full text-left"
          >
            How It Works
          </button>
        </li>
        <li className="nav-item px-6 py-4">
          <button
            onClick={() => scrollToSection('contact-section')}
            className="primary-btn w-full"
          >
            Contact Us
          </button>
        </li>
      </ul>

    </nav>
  );
};

export default Nav;
