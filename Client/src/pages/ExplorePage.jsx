import { useState, useRef, useEffect } from "react";

// Visualization Popup Component
const VisualizationPopup = ({ animalName, onClose }) => {
  const [htmlContent, setHtmlContent] = useState("");
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const loadVisualization = async () => {
      try {
        // Fetch the latest visualization file for this animal
        const response = await fetch(`http://localhost:5000/visualize`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ animal: animalName }),
        });

        if (!response.ok) {
          throw new Error("Failed to load visualization");
        }

        const data = await response.json();
        if (data.success && data.file_path) {
          const vizResponse = await fetch(`/${data.file_path}`);
          const content = await vizResponse.text();
          setHtmlContent(content);
        }
      } catch (error) {
        console.error("Error loading visualization:", error);
        setHtmlContent(`<div class="error">Failed to load visualization for ${animalName}</div>`);
      } finally {
        setIsLoading(false);
      }
    };

    loadVisualization();
  }, [animalName]);

  return (
    <div className="fixed inset-0 z-50 bg-black bg-opacity-75 flex items-center justify-center p-4">
      <div className="relative bg-white rounded-lg w-full max-w-6xl h-[90vh] overflow-auto">
        <button
          onClick={onClose}
          className="absolute top-4 right-4 bg-gray-800 text-white rounded-full p-2 hover:bg-gray-700 z-50"
          aria-label="Close visualization"
        >
          <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
        
        {isLoading ? (
          <div className="flex justify-center items-center h-full">
            <div className="animate-spin rounded-full h-20 w-20 border-b-4 border-gray-800"></div>
          </div>
        ) : (
          <div dangerouslySetInnerHTML={{ __html: htmlContent }} />
        )}
      </div>
    </div>
  );
};

// Species Card Carousel Component
const SpeciesCarousel = ({ speciesData, onVisualize }) => {
  const [isAnimating, setIsAnimating] = useState(false);
  const [displayedIndex, setDisplayedIndex] = useState(0);
  const [animationDirection, setAnimationDirection] = useState(null);
  const carouselRef = useRef(null);

  // Handle navigation
  const goToNext = () => {
    if (isAnimating) return;
    
    setIsAnimating(true);
    setAnimationDirection("next");
    
    setTimeout(() => {
      setDisplayedIndex((prevIndex) => (prevIndex + 1) % Object.keys(speciesData).length);
      setIsAnimating(false);
    }, 300);
  };

  const goToPrev = () => {
    if (isAnimating) return;
    
    setIsAnimating(true);
    setAnimationDirection("prev");
    
    setTimeout(() => {
      setDisplayedIndex((prevIndex) => (prevIndex - 1 + Object.keys(speciesData).length) % Object.keys(speciesData).length);
      setIsAnimating(false);
    }, 300);
  };

  // Early return if no species data
  if (!speciesData || Object.keys(speciesData).length === 0) {
    return <div className="text-center text-gray-400">No species data available</div>;
  }

  // Get current species data
  const speciesNames = Object.keys(speciesData);
  const currentSpeciesName = speciesNames[displayedIndex];
  const currentSpecies = speciesData[currentSpeciesName];
  
  // Safely extract data with fallbacks
  const commonName = currentSpecies?.inaturalist?.name || currentSpeciesName;
  const scientificName = currentSpecies?.inaturalist?.scientific_name || currentSpeciesName;
  const observationsCount = currentSpecies?.inaturalist?.observations_count || "Unknown";
  const conservationStatus = currentSpecies?.inaturalist?.conservation_status || "Not specified";
  const wikipediaUrl = currentSpecies?.inaturalist?.wikipedia_url || null;
  const wikipediaText = currentSpecies?.wikipedia || "No description available.";
  const newsArticles = currentSpecies?.news || [];
  
  // Fixed image URL extraction
  let imageUrl = "https://via.placeholder.com/800";
  if (currentSpecies?.images && Array.isArray(currentSpecies.images) && currentSpecies.images.length > 0) {
    imageUrl = currentSpecies.images[0];
  }

  return (
    <div className="relative w-full h-screen">
      {/* Card content with side-by-side layout */}
      <div 
        ref={carouselRef}
        className={`card-container flex h-full w-full rounded-lg overflow-hidden transition-all duration-300 ease-in-out ${
          isAnimating && animationDirection === "next" ? "transform -translate-x-full opacity-0" : 
          isAnimating && animationDirection === "prev" ? "transform translate-x-full opacity-0" : 
          "transform translate-x-0 opacity-100"
        }`}
      >
        {/* Left side: Content */}
        <div className="flex-1 p-8 md:p-12 overflow-y-auto relative">
          <div className="h-full flex flex-col">
            <div className="mb-6">
              <h2 className="text-5xl md:text-6xl font-bold font-sans text-gray-900 mb-2">{commonName}</h2>
              
              <div className="flex items-center mb-6">
                <p className="text-2xl md:text-3xl italic text-gray-700">{scientificName}</p>
              </div>
              
              <div className="text-gray-600 mb-6 text-lg">
                <div className="flex items-center mb-3">
                  <span className="font-medium text-gray-800 mr-2">Observations:</span>
                  <span>{observationsCount}</span>
                </div>
                <div className="flex items-center mb-3">
                  <span className="font-medium text-gray-800 mr-2">Conservation Status:</span>
                  <span>{conservationStatus}</span>
                </div>
                {wikipediaUrl && (
                  <a 
                    href={wikipediaUrl} 
                    target="_blank" 
                    rel="noopener noreferrer"
                    className="inline-block text-blue-600 hover:text-blue-500 underline mt-1 text-lg"
                  >
                    Wikipedia
                  </a>
                )}
              </div>
              
              <div className="text-gray-600 text-lg mb-8 overflow-y-auto pr-4">
                <p>{wikipediaText.substring(0, 500)}{wikipediaText.length > 500 ? '...' : ''}</p>
              </div>

              {/* Visualization button */}
              <button
                onClick={() => onVisualize(currentSpeciesName)}
                className="bg-blue-600 hover:bg-blue-700 text-white rounded-lg px-6 py-3 text-lg font-medium transition-colors mb-8"
              >
                View Distribution Map
              </button>

              {/* News section */}
              {newsArticles.length > 0 && (
                <div className="mt-6">
                  <h3 className="font-medium text-gray-800 text-xl mb-3">Recent News</h3>
                  <ul className="space-y-3">
                    {newsArticles.slice(0, 3).map((article, index) => (
                      <li key={index}>
                        <a 
                          href={article.link} 
                          target="_blank" 
                          rel="noopener noreferrer"
                          className="text-blue-600 hover:text-blue-500 text-lg"
                        >
                          {article.title}
                        </a>
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          </div>
        </div>
        
        {/* Right side: Image */}
        <div className="w-1/2 relative hidden md:block overflow-hidden">
          <div className="h-full w-full">
            <img 
              src={imageUrl} 
              alt={commonName}
              className="w-full h-full object-cover transition-transform duration-300 hover:scale-105"
              onError={(e) => {
                e.target.onerror = null;
                e.target.src = "https://via.placeholder.com/800?text=No+Image";
              }}
            />
          </div>
        </div>
      </div>
      
      {/* Navigation buttons and counter */}
      {Object.keys(speciesData).length > 1 && (
        <div className="absolute bottom-8 left-0 right-0 flex justify-between items-center px-8">
          <button 
            onClick={goToPrev}
            disabled={isAnimating}
            className={`bg-slate-800 text-white rounded-full p-3 hover:bg-slate-700 transition-all transform hover:-translate-x-1 focus:outline-none focus:ring-2 focus:ring-gray-300 shadow-lg ${isAnimating ? 'opacity-50 cursor-not-allowed' : ''}`}
            aria-label="Previous species"
          >
            <svg xmlns="http://www.w3.org/2000/svg" className="h-8 w-8" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
            </svg>
          </button>
          
          <p className="text-gray-800 text-xl font-medium bg-white bg-opacity-80 px-4 py-2 rounded-full">
            {displayedIndex + 1} of {Object.keys(speciesData).length}
          </p>
          
          <button 
            onClick={goToNext}
            disabled={isAnimating}
            className={`bg-slate-800 text-white rounded-full p-3 hover:bg-slate-700 transition-all transform hover:translate-x-1 focus:outline-none focus:ring-2 focus:ring-gray-300 shadow-lg ${isAnimating ? 'opacity-50 cursor-not-allowed' : ''}`}
            aria-label="Next species"
          >
            <svg xmlns="http://www.w3.org/2000/svg" className="h-8 w-8" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
            </svg>
          </button>
        </div>
      )}
    </div>
  );
};

export default function ExplorePage() {
  const [searchTerm, setSearchTerm] = useState("");
  const [speciesData, setSpeciesData] = useState({});
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [showVisualization, setShowVisualization] = useState(false);
  const [currentAnimal, setCurrentAnimal] = useState("");
  const [hasSearched, setHasSearched] = useState(false); // Add this new state

  const handleSearch = async (event) => {
    event.preventDefault();
    if (!searchTerm.trim()) return; // Don't search if empty
    
    setHasSearched(true); // Mark that a search has been attempted
    setSpeciesData({});
    setIsLoading(true);
    setError(null);

    try {
      const response = await fetch("http://localhost:5000/explore", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ location: searchTerm }),
      });

      if (!response.ok) {
        throw new Error(`Error: ${response.status} ${response.statusText}`);
      }

      const data = await response.json();
      
      if (data.success && data.data) {
        setSpeciesData(data.data);
      } else {
        throw new Error(data.error || "No species data found");
      }
    } catch (error) {
      console.error("Search error:", error);
      setError(error.message);
    } finally {
      setIsLoading(false);
    }
  };

  const handleVisualize = (animalName) => {
    setCurrentAnimal(animalName);
    setShowVisualization(true);
  };

  // For demonstration/testing purposes
  const loadSampleData = () => {
    const sampleData = {
      "Trinket Snake": {
        "images": [
          "https://inaturalist-open-data.s3.amazonaws.com/photos/460916173/original.jpeg"
        ],
        "wikipedia": "The trinket snake (Coelognathus helena), also known commonly as the common trinket snake, is a species of nonvenomous constricting snake in the family Colubridae. The species is native to southern Central Asia. The trinket snake has a slender body with a slightly flattened head and a pointed snout. It typically grows to a length of 3–4 feet (0.9–1.2 m).",
        "inaturalist": {
          "name": "Trinket Snake",
          "scientific_name": "Coelognathus helena",
          "observations_count": 703,
          "conservation_status": "Least Concern",
          "wikipedia_url": "http://en.wikipedia.org/wiki/Trinket_snake"
        }
      },
      "Indian Peafowl": {
        "images": [
          "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c5/Peacock_Plumage.jpg/1200px-Peacock_Plumage.jpg"
        ],
        "wikipedia": "The Indian peafowl (Pavo cristatus) is a peafowl species native to the Indian subcontinent. It has been introduced to many other countries. The male peacock is brightly colored with a predominantly blue fan-like crest of spatula-tipped wire-like feathers and is best known for the long train made up of elongated upper-tail covert feathers which bear colorful eyespots.",
        "inaturalist": {
          "name": "Indian Peafowl",
          "scientific_name": "Pavo cristatus",
          "observations_count": 8942,
          "conservation_status": "Least Concern",
          "wikipedia_url": "http://en.wikipedia.org/wiki/Indian_peafowl"
        }
      },
      "Bengal Tiger": {
        "images": [
          "https://upload.wikimedia.org/wikipedia/commons/thumb/1/17/Tiger_in_Ranthambhore.jpg/1200px-Tiger_in_Ranthambhore.jpg"
        ],
        "wikipedia": "The Bengal tiger is a tiger subspecies native to the Indian subcontinent. It is the most numerous tiger subspecies, with populations in India, Bangladesh, Nepal, Bhutan, and Myanmar. It is listed as Endangered on the IUCN Red List since 2008. The Bengal tiger ranks among the biggest wild cats alive today.",
        "inaturalist": {
          "name": "Bengal Tiger",
          "scientific_name": "Panthera tigris tigris",
          "observations_count": 586,
          "conservation_status": "Endangered",
          "wikipedia_url": "http://en.wikipedia.org/wiki/Bengal_tiger"
        }
      }
    };
    setSpeciesData(sampleData);
  };

  return (
    <div className="w-full h-screen overflow-hidden relative">
      {/* Search form - only shown when no data is loaded */}
      {Object.keys(speciesData).length === 0 && (
        <div className="absolute inset-0 flex items-center justify-center z-10 bg-white">
          <div className="max-w-2xl w-full px-4">
            <form onSubmit={handleSearch} className="mb-10">
              <div className="relative w-full mx-auto">
                <input
                  type="search"
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="block w-full p-4 pl-6 text-gray-900 rounded-full bg-slate-100 ring-1 ring-gray-300 focus:outline-none focus:ring-2 focus:ring-blue-500 text-lg"
                  placeholder="Search a location to explore species..."
                  required
                />
                <button
                  type="submit"
                  className="absolute right-2 top-2 bg-blue-600 hover:bg-blue-700 text-white rounded-full px-6 py-2 font-medium transition-colors"
                >
                  Explore
                </button>
              </div>
            </form>

            {/* Sample data button */}
            <div className="text-center mt-8">
              <button 
                onClick={() => {
                  setHasSearched(false);
                  loadSampleData();
                }}
                className="bg-gray-800 hover:bg-gray-700 text-white rounded-lg px-6 py-3 text-lg font-medium transition-colors"
              >
                Try Sample Data
              </button>
            </div>
          </div>
        </div>
      )}

      {isLoading && (
        <div className="absolute inset-0 flex justify-center items-center z-20 bg-white bg-opacity-80">
          <div className="animate-spin rounded-full h-24 w-24 border-b-4 border-blue-600"></div>
        </div>
      )}

      {error && (
        <div className="absolute inset-0 flex items-center justify-center z-20 bg-white">
          <div className="text-center max-w-2xl px-4">
            <p className="text-red-500 text-xl mb-6">{error}</p>
            <button 
              onClick={() => {
                setHasSearched(false);
                loadSampleData();
              }}
              className="bg-gray-800 hover:bg-gray-700 text-white rounded-lg px-6 py-3 text-lg font-medium transition-colors"
            >
              Load Sample Data
            </button>
          </div>
        </div>
      )}

      {/* Modified this condition to only show when a search was attempted */}
      {!isLoading && hasSearched && Object.keys(speciesData).length === 0 && !error && (
        <div className="absolute inset-0 flex items-center justify-center z-10 bg-white">
          <p className="text-gray-500 text-xl">No species found for this location. Try another search.</p>
        </div>
      )}

      {/* Main content - species carousel */}
      {!isLoading && Object.keys(speciesData).length > 0 && (
        <SpeciesCarousel 
          speciesData={speciesData} 
          onVisualize={handleVisualize} 
        />
      )}

      {/* Visualization popup */}
      {showVisualization && (
        <VisualizationPopup 
          animalName={currentAnimal} 
          onClose={() => setShowVisualization(false)} 
        />
      )}
    </div>
  );
}