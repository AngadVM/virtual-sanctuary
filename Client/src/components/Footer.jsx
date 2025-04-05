import React from "react";
import tvsFullLogo from "@assets/tvs-full-logo.svg";


function Footer() {
  return (
    <div>
      <footer className="w-4xl">
        <div className="w-full max-w-screen-xl mx-auto p-4 md:py-8">
          <div className="sm:flex sm:items-center sm:justify-between">
            <a
              href="/"
              className="flex items-center mb-4 sm:mb-0 space-x-3 rtl:space-x-reverse"
            >
              <img src={tvsFullLogo} className="h-16" alt="Flowbite Logo" />
            </a>
            <ul className="flex flex-wrap items-center mb-6 text-sm font-medium text-gray-500 sm:mb-0 dark:text-gray-400">
              <li>
                <a href="" className="hover:underline me-4 md:me-6">
                  About
                </a>
              </li>
              <li>
                <a href="" className="hover:underline me-4 md:me-6">
                  Blogs
                </a>
              </li>
              <li>
                <a href="" className="hover:underline me-4 md:me-6">
                  Explore
                </a>
              </li>
              <li>
                <a href="/register" className="hover:underline">
                  Register
                </a>
              </li>
            </ul>
          </div>
          <hr className="my-6 border-gray-200 sm:mx-auto dark:border-gray-700 lg:my-8" />
          <span className="block text-sm text-gray-500 sm:text-center dark:text-gray-400">
            Copyright © 2025{" "}
            <a href="/" className="hover:underline">
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
