"use client";

import Image from "next/image";
import { InstagramIcon, LinkedinIcon } from "lucide-react";

const Footer = () => {
  const scrollToSection = (id) => {
    const el = document.getElementById(id);
    if (el) {
      el.scrollIntoView({ behavior: "smooth" });
    }
  };

  return (
    <footer className="border-t container border-gray-400 py-10 px-4 md:px-10 z-20">
      {/* Top row: logo + socials */}
      <div className="flex flex-row items-center justify-between mb-4 md:mb-10">
        <a href="/" className="mb-6 md:mb-0">
          <div className="relative aspect-[819/304] w-[190px] h-[70px]">
            <Image
              src="/images/faceframe_logo2.png"
              alt="Footer Logo"
              fill
              className="object-contain"
            />
          </div>
        </a>

        <div className="flex gap-4">
          <a
            href="https://www.instagram.com/faceframe.ai/"
            target="_blank"
            rel="noopener noreferrer"
            className="hover:cursor-pointer"
          >
            <button className="primary-btn h-auto! p-3! rounded-full! sm:w-auto">
              <InstagramIcon className="h-5 w-5" />
            </button>
          </a>

          <a
            href="https://www.linkedin.com/company/faceframe/"
            target="_blank"
            rel="noopener noreferrer"
            className="hover:cursor-pointer"
          >
            <button className="primary-btn h-auto! p-3! rounded-full! sm:w-auto">
              <LinkedinIcon className="h-5 w-5"/>
            </button>
          </a>
        </div>
      </div>

      <hr className="border-[0.5px] border-gray-400 mb-8 w-full" />


      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div className="text-[14px] md:text-base text-gray-600 text-center order-last md:order-first md:text-left">
          &copy; 2025 FaceFrame. <br className="hidden md:block" /> All rights reserved.
        </div>

        <ul className="flex flex-col md:flex-row justify-center md:justify-end gap-4 md:gap-2">
          <li className="footer-item">
            <button
              onClick={() => scrollToSection("features-section")}
              className="footer-nav-link cursor-pointer"
            >
              Features
            </button>
          </li>
          <li className="footer-item">
            <button
              onClick={() => scrollToSection("about-section")}
              className="footer-nav-link cursor-pointer"
            >
              About
            </button>
          </li>
          <li className="footer-item">
            <button
              onClick={() => scrollToSection("how-it-works-section")}
              className="footer-nav-link cursor-pointer"
            >
              How It Works
            </button>
          </li>
          <li className="footer-item">
            <button
              onClick={() => scrollToSection("contact-section")}
              className="footer-nav-link cursor-pointer"
            >
              Contact
            </button>
          </li>
        </ul>
      </div>
    </footer>
  );
};

export default Footer;
