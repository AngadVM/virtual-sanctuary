import { useState, useEffect } from "react";

export default function ExplorePage() {
    const [searchTerm, setSearchTerm] = useState("");
    const [speciesList, setSpeciesList] = useState([]);
    const [isLoading, setIsLoading] = useState(false);

    const handleSearch = async (event) => {
      event.preventDefault();
      setSpeciesList([]); // Clear previous results
      setIsLoading(true);
  
      const response = await fetch("http://localhost:5000/explore", {
          method: "POST",
          headers: {
              "Content-Type": "application/json",
          },
          body: JSON.stringify({ location: searchTerm }),
      });
  
      if (!response.ok) {
          console.error("Error fetching data:", response.statusText);
          setIsLoading(false);
          return;
      }
  
      const reader = response.body.getReader();
      const decoder = new TextDecoder("utf-8");
  
      while (true) {
          const { done, value } = await reader.read();
          if (done) break;
  
          const decodedText = decoder.decode(value);
          const speciesArray = decodedText.split("\n\n").filter(Boolean);
  
          speciesArray.forEach((speciesText) => {
              if (speciesText.startsWith("data:")) {
                  const jsonString = speciesText.replace("data:", "").trim();
                  try {
                      const speciesData = JSON.parse(jsonString);
                      setSpeciesList((prev) => [...prev, speciesData]);
                  } catch (error) {
                      console.error("Error parsing species JSON:", error);
                  }
              }
          });
      }
  
      setIsLoading(false);
  };
  

    return (
        <div className="max-w-md mx-auto my-6">
            <form onSubmit={handleSearch}>
                <div className="relative">
                    <input
                        type="search"
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
            </form>

            {isLoading && <p className="mt-4 text-white">Loading species data...</p>}

            <ul className="mt-4 text-white">
    {speciesList.map((species, index) => (
        <li key={index}>
            <pre className="bg-gray-800 p-2 rounded">{JSON.stringify(species, null, 2)}</pre>
        </li>
    ))}
</ul>

        </div>
    );
}
