import React from "react";
import tvsFullLogo from "@assets/tvs-full-logo.svg";

const scrollToAbout = (e) => {
  e.preventDefault();
  const aboutSection = document.querySelector('.about');
  if (aboutSection) {
    aboutSection.scrollIntoView({ behavior: 'smooth' });
  }
};

function Footer() {
  return (
    <div>
      <footer class="bg-black rounded-lg shadow-sm dark:bg-black m-4">
        <div class="w-full max-w-screen-xl mx-auto p-4 md:py-8">
          <div class="sm:flex sm:items-center sm:justify-between">
            <a
              href="/"
              class="flex items-center mb-4 sm:mb-0 space-x-3 rtl:space-x-reverse"
            >
              <img src={tvsFullLogo} class="h-16" alt="Flowbite Logo" />
            </a>
            <ul class="flex flex-wrap items-center mb-6 text-sm font-medium text-gray-500 sm:mb-0 dark:text-gray-400">
              <li>
                <a href="#about" onClick={scrollToAbout} class="hover:underline me-4 md:me-6">
                  About
                </a>
              </li>
              <li>
                <a href="#" class="hover:underline me-4 md:me-6">
                  Contact Support
                </a>
              </li>
              <li>
                <a href="/references" class="hover:underline me-4 md:me-6">
                  References
                </a>
              </li>
              <li>
                <a href="/register" class="hover:underline">
                  Register
                </a>
              </li>
            </ul>
          </div>
          <hr class="my-6 border-gray-200 sm:mx-auto dark:border-gray-700 lg:my-8" />
          <span class="block text-sm text-gray-500 sm:text-center dark:text-gray-400">
            Copyright © 2025{" "}
            <a href="/" class="hover:underline">
              Virtuary
            </a>
            &#9;| Made with &#10084; &#9;| All Rights Reserved.
          </span>
        </div>
      </footer>
    </div>
  );
}

export default Footer;
