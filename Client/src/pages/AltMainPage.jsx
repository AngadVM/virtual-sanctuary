import React from "react";
import "../App.css";
import video from "@assets/video.mp4";
import { Link } from "react-router-dom";
import tvsLogo from "@assets/tvs-logo.svg";

const AltMainPage = () => {
  const navigation = [
    { name: "Write Blog", href: "/write" },
    { name: "Explore", href: "/explore" },
    { name: "Gallery", href: "/gallery" },
  ];

  return (
    <div className="relative w-full h-screen overflow-hidden flex items-center justify-center">
      {/* Background Video */}
      <video
        autoPlay
        loop
        muted
        playsInline
        className="absolute top-0 left-0 w-full h-full object-cover -z-10"
      >
        <source src={video} type="video/mp4" />
        Your browser does not support the video tag.
      </video>

      {/* Content */}
      <div className="relative w-full h-full bg-black/10 rounded-lg flex flex-col">
        {/* Header */}
        <header className="absolute inset-x-0 top-0 z-50">
          <nav className="flex items-center justify-between p-6 lg:px-8">
            <div className="flex lg:flex-1">
              <Link to="/" className="-m-1.5 p-1.5">
                <span className="sr-only">Your Company</span>
                <img src={tvsLogo} alt="" className="h-12 w-auto" />
              </Link>
            </div>
            {/* <div className="hidden lg:flex lg:gap-x-12">
              {navigation.map((item) => (
                <Link
                  key={item.name}
                  to={item.href}
                  className="text-sm font-semibold text-gray-200 hover:underline"
                >
                  {item.name}
                </Link>
              ))}
            </div> */}
            <div className="hidden lg:flex lg:flex-1 lg:justify-end">
              <Link to="/login" className="text-sm font-semibold text-gray-200">
                Sign in <span aria-hidden="true">&rarr;</span>
              </Link>
            </div>
          </nav>
        </header>

        {/* Main Content */}
        <div className="relative px-6 lg:px-8 flex flex-col items-center justify-center h-full text-center">
          <div className="max-w-2xl">
            <div className="hidden sm:mb-8 sm:flex sm:justify-center">
              <div className="relative rounded-full px-3 py-1 text-sm text-gray-400 ring-1 ring-gray-300/10 hover:ring-gray-300/20">
                This project is open source.{" "}
                <a
                  href="https://github.com/MuizZatam/virtual-sanctuary"
                  className="font-semibold text-gray-200 hover:underline"
                  target="_blank"
                  rel="noreferrer"
                >
                  Contribute <span aria-hidden="true">&rarr;</span>
                </a>  
              </div>
            </div>
            <h1 className="text-6xl font-bold tracking-tight text-gray-100 sm:text-5xl">
              Discover the untamed beauty of wildlife virtually.
            </h1>
            <p className="mt-8 text-md font-medium text-gray-400 sm:text-lg">
              Explore our virtual wildlife sanctuary and witness real-time
              conservation status updates and connect with nature's finest
              creatures.
            </p>
            <div className="mt-10 flex items-center justify-center gap-x-6">
              <a href="/login" className="rounded-md bg-gray-200 px-3.5 py-2 text-sm font-semibold text-black shadow-xs hover:bg-gray-300 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-gray-600">
                Get started
              </a>
              <a
                to="/learn-more"
                className="text-sm font-semibold text-gray-100 hover:underline"
              >
                Learn more <span aria-hidden="true">→</span>
              </a>
            </div>
          </div>
          <br />
          <footer class="w-5xl rounded-lg shadow-sm mt-40 border-gray-600 bottom-4 absolute">
            <div class="w-full mx-auto max-w-screen-xl p-4 md:flex md:items-center md:justify-between">
              <span class="text-sm text-gray-300 sm:text-center dark:text-gray-300">
                © 2025{" "}
                <a href="/" class="hover:underline font-black">
                  Virtuary
                </a>
                . All Rights Reserved.
              </span>
              <ul class="flex flex-wrap items-center mt-3 text-sm font-medium text-gray-500 dark:text-gray-400 sm:mt-0">
                <li>
                  <a href="/about" class="hover:underline me-4 md:me-6">
                    About
                  </a>
                </li>
                <li>
                  <a href="/" class="hover:underline me-4 md:me-6">
                    Blogs
                  </a>
                </li>
                <li>
                  <a href="/explore" class="hover:underline me-4 md:me-6">
                    Explore
                  </a>
                </li>
                <li>
                  <a href="/login" class="hover:underline">
                    Log in
                  </a>
                </li>
              </ul>
            </div>
          </footer>
        </div>
      </div>
    </div>
  );
};

export default AltMainPage;
