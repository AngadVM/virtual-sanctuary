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
            <div className="hidden lg:flex lg:flex-1 lg:justify-end ">
              <Link to="https://github.com/MuizZatam/virtual-sanctuary" target="__blank" className="text-sm h-10">
                <svg width="40" height="40" viewBox="0 -3.5 256 256" xmlns="http://www.w3.org/2000/svg" preserveAspectRatio="xMinYMin meet">

                  <g fill="#ffffff">

                    <path d="M127.505 0C57.095 0 0 57.085 0 127.505c0 56.336 36.534 104.13 87.196 120.99 6.372 1.18 8.712-2.766 8.712-6.134 0-3.04-.119-13.085-.173-23.739-35.473 7.713-42.958-15.044-42.958-15.044-5.8-14.738-14.157-18.656-14.157-18.656-11.568-7.914.872-7.752.872-7.752 12.804.9 19.546 13.14 19.546 13.14 11.372 19.493 29.828 13.857 37.104 10.6 1.144-8.242 4.449-13.866 8.095-17.05-28.32-3.225-58.092-14.158-58.092-63.014 0-13.92 4.981-25.295 13.138-34.224-1.324-3.212-5.688-16.18 1.235-33.743 0 0 10.707-3.427 35.073 13.07 10.17-2.826 21.078-4.242 31.914-4.29 10.836.048 21.752 1.464 31.942 4.29 24.337-16.497 35.029-13.07 35.029-13.07 6.94 17.563 2.574 30.531 1.25 33.743 8.175 8.929 13.122 20.303 13.122 34.224 0 48.972-29.828 59.756-58.22 62.912 4.573 3.957 8.648 11.717 8.648 23.612 0 17.06-.148 30.791-.148 34.991 0 3.393 2.295 7.369 8.759 6.117 50.634-16.879 87.122-64.656 87.122-120.973C255.009 57.085 197.922 0 127.505 0" />

                    <path d="M47.755 181.634c-.28.633-1.278.823-2.185.389-.925-.416-1.445-1.28-1.145-1.916.275-.652 1.273-.834 2.196-.396.927.415 1.455 1.287 1.134 1.923M54.027 187.23c-.608.564-1.797.302-2.604-.589-.834-.889-.99-2.077-.373-2.65.627-.563 1.78-.3 2.616.59.834.899.996 2.08.36 2.65M58.33 194.39c-.782.543-2.06.034-2.849-1.1-.781-1.133-.781-2.493.017-3.038.792-.545 2.05-.055 2.85 1.07.78 1.153.78 2.513-.019 3.069M65.606 202.683c-.699.77-2.187.564-3.277-.488-1.114-1.028-1.425-2.487-.724-3.258.707-.772 2.204-.555 3.302.488 1.107 1.026 1.445 2.496.7 3.258M75.01 205.483c-.307.998-1.741 1.452-3.185 1.028-1.442-.437-2.386-1.607-2.095-2.616.3-1.005 1.74-1.478 3.195-1.024 1.44.435 2.386 1.596 2.086 2.612M85.714 206.67c.036 1.052-1.189 1.924-2.705 1.943-1.525.033-2.758-.818-2.774-1.852 0-1.062 1.197-1.926 2.721-1.951 1.516-.03 2.758.815 2.758 1.86M96.228 206.267c.182 1.026-.872 2.08-2.377 2.36-1.48.27-2.85-.363-3.039-1.38-.184-1.052.89-2.105 2.367-2.378 1.508-.262 2.857.355 3.049 1.398" />

                  </g>

                </svg>
              </Link>
            </div>
          </nav>
        </header>

        {/* Main Content */}
        <div className="relative px-6 lg:px-8 flex flex-col items-center justify-center h-full text-center">
          <div className="max-w-2xl">
            <div className="hidden sm:mb-8 sm:flex sm:justify-center">
              {/* <div className="relative rounded-full px-3 py-1 text-sm text-gray-500">
                This project is open source, {" "}
                <a
                  href="https://github.com/MuizZatam/virtual-sanctuary"
                  className="font-semibold text-gray-300 underline underline-offset-4"
                  target="_blank"
                  rel="noreferrer"
                >
                  contribute here
                </a>  
              </div> */}
            </div>
            <h1 className="text-6xl font-bold tracking-tight text-gray-100 sm:text-5xl">
              Discover the untamed beauty of wildlife virtually.
            </h1>
            <p className="mt-8 text-md font-medium text-gray-300/50 sm:text-lg">
              Explore our virtual wildlife sanctuary and witness real-time
              conservation status updates and connect with nature's finest
              creatures.
            </p>
            <div className="mt-10 flex items-center justify-center gap-x-6">
              <a href="/register" className="rounded-full px-3.5 py-2 text-md bg-white/10 font-medium  text-white shadow-xs hover:bg-white hover:text-black transition duration-500 ease-in-out outline-1 focus-visible:outline-offset-2 focus-visible:outline-gray-600">
                Get started  <span aria-hidden="true">&rarr;</span>
              </a>
              {/* <a
                to="/learn-more"
                className="text-sm font-semibold text-gray-100 hover:underline"
              >
                Learn more <span aria-hidden="true">→</span>
              </a> */}
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
                  <a href="/explore" class="underline underline-offset-2 me-4 md:me-6">
                    Explore
                  </a>
                </li>
                <li>
                  <a href="/write" class="underline underline-offset-2 me-4 md:me-6">
                    Blogs
                  </a>
                </li>
                <li>
                  <a href="/gallery" class="underline underline-offset-2 me-4 md:me-6">
                    Gallery
                  </a>
                </li>
                <li>
                  <a href="/login" class="underline underline-offset-2 ">
                    Privacy Policy
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
