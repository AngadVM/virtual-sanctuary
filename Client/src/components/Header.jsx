import React from "react";
import virtuaryFullLogo from "../assets/tvs-full-logo.svg";

function Header() {
  const styles = {
    underlineText: {
      textDecoration: "underline",
    },
  };
  return (
    <>
      <header className="header rounded-4xl my-6">
        <div className="container mx-auto flex flex-wrap p-5 flex-col md:flex-row items-center">
          <a className="flex title-font font-medium items-center text-white mb-4 md:mb-0">
            <img src={virtuaryFullLogo} alt="" />
          </a>
          <nav className="md:ml-auto md:mr-auto flex flex-wrap items-center text-base justify-center">
            <a style={styles.underlineText} className="mr-10">
              Explore
            </a>
            <a style={styles.underlineText} className="mr-10">
              Blog
            </a>
            <a style={styles.underlineText} className="mr-10">
              Gallery
            </a>
          </nav>
          <button className="inline-flex items-center font-bold border-0 py-1 px-3 bg-blue-500 focus:outline-none rounded-xl text-base mt-4 md:mt-0">
            Sign In
          </button>
        </div>
      </header>
    </>
  );
}

export default Header;
