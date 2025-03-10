import React from "react";
import {
  BrowserRouter,
  Routes,
  Route,
  Navigate,
  Link,
  useNavigate,
} from "react-router-dom";
import { useState } from "react";
import { Dialog, DialogPanel } from "@headlessui/react";
import { Bars3Icon, XMarkIcon } from "@heroicons/react/24/outline";
import virtuaryLogo from "@assets/tvs-logo.svg";

const AuthContext = React.createContext(null);

const AuthProvider = ({ children }) => {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const login = () => setIsAuthenticated(true);
  const logout = () => setIsAuthenticated(false);

  return (
    <AuthContext.Provider value={{ isAuthenticated, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
};

const ProtectedRoute = ({ children }) => {
  const { isAuthenticated } = React.useContext(AuthContext);
  if (!isAuthenticated) return <Navigate to="/login" replace />;
  return children;
};

// Components for other pages with matching black background
const Login = () => {
  const { login } = React.useContext(AuthContext);
  const navigate = useNavigate();

  return (
    <div className="bg-black min-h-screen">
      <div className="mx-auto max-w-2xl py-32">
        <div className="text-center">
          <h2 className="text-xl font-semibold text-gray-200 mb-4">Sign In</h2>
          <button
            onClick={() => {
              login();
              navigate("/");
            }}
            className="rounded-md bg-gray-200 px-3.5 py-2.5 text-sm font-semibold text-black shadow-xs hover:bg-gray-300"
          >
            Sign In
          </button>
        </div>
      </div>
    </div>
  );
};

const Explore = () => {
  const [searchTerm, setSearchTerm] = useState("");
  const [result, setResult] = useState(null);

  const handleSearch = async (event) => {
    event.preventDefault();

    try {
      const response = await fetch("http://localhost:5000/explore", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ location: searchTerm }),
      });

      const data = await response.json();
      console.log("Backend Response:", data); // Log response

      setResult(data);
    } catch (error) {
      console.error("Error fetching data:", error);
    }
  };

  return (
    <form onSubmit={handleSearch} className="max-w-md mx-auto">
      <label htmlFor="default-search" className="sr-only">
        Search
      </label>
      <div className="relative">
        <input
          type="search"
          id="default-search"
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          className="block w-full p-4 ps-10 text-sm text-gray-900 border border-gray-300 rounded-lg bg-gray-50"
          placeholder="Search a location..."
          required
        />
        <button
          type="submit"
          className="absolute end-2.5 bottom-2.5 bg-blue-700 text-white rounded-lg px-4 py-2"
        >
          Search
        </button>
      </div>
      {result && (
        <div className="mt-4 p-4 bg-gray-100 rounded-md">
          <pre>{JSON.stringify(result, null, 2)}</pre>
        </div>
      )}
    </form>
  );
};

const LearnMore = () => (
  <div className="bg-black min-h-screen">
    <div className="mx-auto max-w-2xl py-32">
      <div className="text-center">
        <h2 className="text-xl font-semibold text-gray-200">Learn more Page</h2>
      </div>
    </div>
  </div>
);

const WriteBlog = () => (
  <div className="bg-black min-h-screen">
    <div className="mx-auto max-w-2xl py-32">
      <div className="text-center">
        <h2 className="text-xl font-semibold text-gray-200">Write Blog Page</h2>
      </div>
    </div>
  </div>
);

const Gallery = () => (
  <div className="bg-black min-h-screen">
    <div className="mx-auto max-w-2xl py-32">
      <div className="text-center">
        <h2 className="text-xl font-semibold text-gray-200">Gallery Page</h2>
      </div>
    </div>
  </div>
);

const HeroSection = () => {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const { isAuthenticated, logout } = React.useContext(AuthContext);
  const navigate = useNavigate();

  const navigation = [
    { name: "Write Blog", href: "/write" },
    { name: "Explore", href: "/explore" },
    { name: "Gallery", href: "/gallery" },
  ];

  return (
    <div className="bg-black">
      <header className="absolute inset-x-0 top-0 z-50">
        <nav
          className="flex items-center justify-between p-6 lg:px-8"
          aria-label="Global"
        >
          <div className="flex lg:flex-1">
            <Link to="/" className="-m-1.5 p-1.5">
              <span className="sr-only">Your Company</span>
              <img src={virtuaryLogo} alt="" className="h-12 w-auto" />
            </Link>
          </div>
          <div className="flex lg:hidden">
            <button
              type="button"
              className="-m-2.5 inline-flex items-center justify-center rounded-md p-2.5 text-gray-200"
              onClick={() => setMobileMenuOpen(true)}
            >
              <span className="sr-only">Open main menu</span>
              <Bars3Icon className="size-6" aria-hidden="true" />
            </button>
          </div>
          <div className="hidden lg:flex lg:gap-x-12">
            {navigation.map((item) => (
              <Link
                key={item.name}
                to={item.href}
                className="text-sm/6 font-semibold text-gray-200 hover:underline"
              >
                {item.name}
              </Link>
            ))}
          </div>
          <div className="hidden lg:flex lg:flex-1 lg:justify-end">
            {isAuthenticated ? (
              <button
                onClick={() => {
                  logout();
                  navigate("/");
                }}
                className="text-sm/6 font-semibold text-gray-200"
              >
                Sign out <span aria-hidden="true">&rarr;</span>
              </button>
            ) : (
              <Link
                to="/login"
                className="text-sm/6 font-semibold text-gray-200"
              >
                Log in <span aria-hidden="true">&rarr;</span>
              </Link>
            )}
          </div>
        </nav>
        <Dialog
          as="div"
          className="lg:hidden"
          open={mobileMenuOpen}
          onClose={setMobileMenuOpen}
        >
          <div className="fixed inset-0 z-50" />
          <DialogPanel className="fixed inset-y-0 right-0 z-50 w-full overflow-y-auto bg-black px-6 py-6 sm:max-w-sm sm:ring-1 sm:ring-gray-200">
            <div className="flex items-center justify-between">
              <Link to="/" className="-m-1.5 p-1.5">
                <span className="sr-only">Your Company</span>
                <img src={virtuaryLogo} alt="" className="h-8 w-auto" />
              </Link>
              <button
                type="button"
                className="-m-2.5 rounded-md p-2.5 text-gray-200"
                onClick={() => setMobileMenuOpen(false)}
              >
                <span className="sr-only">Close menu</span>
                <XMarkIcon className="size-6" aria-hidden="true" />
              </button>
            </div>
            <div className="mt-6 flow-root">
              <div className="-my-6 divide-y divide-gray-200/10">
                <div className="space-y-2 py-6">
                  {navigation.map((item) => (
                    <Link
                      key={item.name}
                      to={item.href}
                      className="-mx-3 block rounded-lg px-3 py-2 text-base/7 font-semibold text-gray-200"
                      onClick={() => setMobileMenuOpen(false)}
                    >
                      {item.name}
                    </Link>
                  ))}
                </div>
                <div className="py-6">
                  {isAuthenticated ? (
                    <button
                      onClick={() => {
                        logout();
                        navigate("/");
                        setMobileMenuOpen(false);
                      }}
                      className="-mx-3 block rounded-lg px-3 py-2.5 text-base/7 font-semibold text-gray-200"
                    >
                      Sign out
                    </button>
                  ) : (
                    <Link
                      to="/login"
                      className="-mx-3 block rounded-lg px-3 py-2.5 text-base/7 font-semibold text-gray-200"
                      onClick={() => setMobileMenuOpen(false)}
                    >
                      Log in
                    </Link>
                  )}
                </div>
              </div>
            </div>
          </DialogPanel>
        </Dialog>
      </header>

      <div className="relative isolate px-6 pt-14 lg:px-8">
        <div
          className="absolute inset-x-0 -top-40 -z-10 transform-gpu overflow-hidden blur-3xl sm:-top-80"
          aria-hidden="true"
        >
          <div
            className="relative left-[calc(50%-11rem)] aspect-1155/678 w-[36.125rem] -translate-x-1/2 rotate-[30deg] bg-linear-to-tr from-[#41badc] to-[#33e270] opacity-30 sm:left-[calc(50%-30rem)] sm:w-[72.1875rem]"
            style={{
              clipPath:
                "polygon(74.1% 44.1%, 100% 61.6%, 97.5% 26.9%, 85.5% 0.1%, 80.7% 2%, 72.5% 32.5%, 60.2% 62.4%, 52.4% 68.1%, 47.5% 58.3%, 45.2% 34.5%, 27.5% 76.7%, 0.1% 64.9%, 17.9% 100%, 27.6% 76.8%, 76.1% 97.7%, 74.1% 44.1%)",
            }}
          />
        </div>
        <div className="mx-auto max-w-2xl py-32 sm:py-48 lg:py-56">
          <div className="hidden sm:mb-8 sm:flex sm:justify-center">
            <div className="relative rounded-full px-3 py-1 text-sm/6 text-gray-500 ring-1 ring-gray-900/10 hover:ring-gray-900/20">
              This project is open source.{" "}
              <a
                href="https://github.com/MuizZatam/virtual-sanctuary"
                className="font-semibold text-gray-200 hover:underline"
                target="_blank"
              >
                <span className="absolute inset-0" aria-hidden="true" />
                Contribute <span aria-hidden="true">&rarr;</span>
              </a>
            </div>
          </div>
          <div className="text-center">
            <h1 className="text-6xl font-semibold tracking-tight text-balance text-gray-200 sm:text-6xl">
              Discover the untamed beauty of wildlife virtually.
            </h1>
            <p className="mt-8 text-lg font-medium text-pretty text-gray-500 sm:text-xl/8">
              Explore our virtual wildlife sanctuary where endangered species
              find digital refuge. Witness real-time conservation status updates
              and connect with nature's finest creatures.
            </p>
            <div className="mt-10 flex items-center justify-center gap-x-6">
              <Link
                to={isAuthenticated ? "/explore" : "/login"}
                className="rounded-md bg-gray-200 px-3.5 py-2.5 text-sm font-semibold text-black shadow-xs hover:bg-gray-300 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-gray-600"
              >
                Get started
              </Link>
              <Link
                to="/learn-more"
                className="text-sm/6 font-semibold text-gray-200 hover:underline"
              >
                Learn more <span aria-hidden="true">→</span>
              </Link>
            </div>
          </div>
        </div>
        <div
          className="absolute inset-x-0 top-[calc(100%-13rem)] -z-10 transform-gpu overflow-hidden blur-3xl sm:top-[calc(100%-30rem)]"
          aria-hidden="true"
        >
          <div
            className="relative left-[calc(50%+3rem)] aspect-1155/678 w-[36.125rem] -translate-x-1/2 bg-linear-to-tr from-[#92d9ed] to-[#76C893] opacity-30 sm:left-[calc(50%+36rem)] sm:w-[72.1875rem]"
            style={{
              clipPath:
                "polygon(74.1% 44.1%, 100% 61.6%, 97.5% 26.9%, 85.5% 0.1%, 80.7% 2%, 72.5% 32.5%, 60.2% 62.4%, 52.4% 68.1%, 47.5% 58.3%, 45.2% 34.5%, 27.5% 76.7%, 0.1% 64.9%, 17.9% 100%, 27.6% 76.8%, 76.1% 97.7%, 74.1% 44.1%)",
            }}
          />
        </div>
      </div>
    </div>
  );
};

const App = () => {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<HeroSection />} />
          <Route path="/login" element={<Login />} />
          <Route
            path="/write"
            element={
              <ProtectedRoute>
                <WriteBlog />
              </ProtectedRoute>
            }
          />
          <Route path="/explore" element={<Explore />} />
          <Route path="/gallery" element={<Gallery />} />
          <Route path="/learn-more" element={<LearnMore />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
};

export default App;
