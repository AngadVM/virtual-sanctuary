import { useState } from "react";

export default function ExplorePage() {
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
    <form onSubmit={handleSearch} className="max-w-md mx-auto my-6">
      <label htmlFor="default-search" className="sr-only">
        Search
      </label>
      <div className="relative">
        <div class="absolute inset-y-0 start-0 flex items-center ps-3 pointer-events-none">
          <svg
            class="w-4 h-4 text-gray-500 dark:text-gray-400"
            aria-hidden="true"
            xmlns="http://www.w3.org/2000/svg"
            fill="none"
            viewBox="0 0 20 20"
          >
            <path
              stroke="currentColor"
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="m19 19-4-4m0-7A7 7 0 1 1 1 8a7 7 0 0 1 14 0Z"
            />
          </svg>
        </div>
        <input
          type="search"
          id="default-search"
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          className="block w-full p-4 ps-10 text-sm text-gray-300 rounded-lg bg-slate-900"
          placeholder="Search a location..."
          required
        />
        <button
          type="submit"
          className="absolute end-2.5 bottom-2.5 bg-blue-500 text-white rounded-lg px-4 py-1.5"
        >
          Search
        </button>
      </div>
      {result && (
        <div className="mt-4 p-4">
          <pre>{JSON.stringify(result, null, 2)}</pre>
        </div>
      )}
    </form>
  );
}
