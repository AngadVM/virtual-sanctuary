import { useState, useRef, useEffect } from "react";

// Species Card Carousel Component
const SpeciesCarousel = ({ speciesList }) => {
  const [currentIndex, setCurrentIndex] = useState(0);
  const [isPlaying, setIsPlaying] = useState(false);
  const [isAnimating, setIsAnimating] = useState(false);
  const audioRef = useRef(null);
  const [displayedIndex, setDisplayedIndex] = useState(0);
  const [animationDirection, setAnimationDirection] = useState(null);

  // Handle navigation
  const goToNext = () => {
    
    setIsAnimating(true);
    setAnimationDirection("next");
    
    setTimeout(() => {
      setDisplayedIndex((prevIndex) => (prevIndex + 1) % speciesList.length);
      setIsAnimating(false);
    }, 1000);
  };

  const goToPrev = () => {
    if (isAnimating) return;
    
    setIsAnimating(true);
    setAnimationDirection("prev");
    
    setTimeout(() => {
      setDisplayedIndex((prevIndex) => (prevIndex - 1 + speciesList.length) % speciesList.length);
      setIsAnimating(false);
    }, 1000);
  };

  // Handle audio playback
  const toggleAudio = (audioUrl) => {
    if (!audioUrl) return;
    
    if (isPlaying) {
      audioRef.current.pause();
    } else {
      audioRef.current.src = audioUrl;
      audioRef.current.play();
    }
    setIsPlaying(!isPlaying);
  };

  // Reset audio state when changing cards
  useEffect(() => {
    setIsPlaying(false);
    if (audioRef.current) {
      audioRef.current.pause();
    }
  }, [displayedIndex]);

  // Early return if no species data
  if (!speciesList || speciesList.length === 0) {
    return <div className="text-center text-gray-400">No species data available</div>;
  }

  // Get current species data
  const currentSpecies = speciesList[displayedIndex];
  const speciesKey = Object.keys(currentSpecies)[0];
  const speciesData = currentSpecies[speciesKey];
  
  // Safely extract data with fallbacks
  const commonName = speciesData?.inaturalist?.name || speciesKey;
  const scientificName = speciesData?.inaturalist?.scientific_name || speciesKey;
  const observationsCount = speciesData?.inaturalist?.observations_count || "Unknown";
  const conservationStatus = speciesData?.inaturalist?.conservation_status || "Not specified";
  const wikipediaUrl = speciesData?.inaturalist?.wikipedia_url || null;
  const wikipediaText = speciesData?.wikipedia || "No description available.";
  
  // Fixed image URL extraction
  let imageUrl = "https://via.placeholder.com/800";
  if (speciesData && speciesData.images && Array.isArray(speciesData.images) && speciesData.images.length > 0) {
    imageUrl = speciesData.images[0];
  }
  
  // Fixed audio URL extraction
  let audioUrl = null;
  if (speciesData && speciesData.audio && Array.isArray(speciesData.audio) && speciesData.audio.length > 0) {
    audioUrl = speciesData.audio[0];
  }

  return (
    <div className="relative w-full">
      {/* Hidden audio element */}
      <audio ref={audioRef} onEnded={() => setIsPlaying(false)} />
      
      {/* Card content with side-by-side layout */}
      <div 
        className={`card-container flex -mt-8 h-full w-full rounded-lg overflow-hidden transition-all duration-1000 ${
          isAnimating && animationDirection === "next" ? "slide-out-left" : 
          isAnimating && animationDirection === "prev" ? "slide-out-right" : ""
        }`} 
        style={{ height: "32rem" }}
      >
        {/* Left side: Content */}
        <div className="flex-1 p-6 md:p-8 overflow-y-auto relative">
          <div className="h-full flex flex-col">
            <div className="mb-4">
              <h2 className="text-5xl font-semibold font-sans text-gray-900 mb-1">{commonName}</h2>
              
              <div className="flex items-center mb-4">
                <p className="text-xl pt-2 italic text-gray-700">{scientificName}</p>
                
                {audioUrl && (
                  <button 
                    onClick={() => toggleAudio(audioUrl)} 
                    className={`ml-4 mt-2 p-1 rounded-full ${
                      isPlaying 
                        ? "bg-green-800 hover:bg-green-700" 
                        : "bg-gray-800 hover:bg-gray-700"
                    } transition-colors flex items-center`}
                    aria-label={isPlaying ? "Pause audio" : "Play audio"}
                  >
                    {isPlaying ? (
                      <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 9v6m4-6v6m7-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                      </svg>
                    ) : (
                      <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z" />
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                      </svg>
                    )}
                  </button>
                )}
              </div>
              
              <div className="text-gray-500 mb-4">
                <div className="flex items-center mb-1">
                  <span className="font-medium text-gray-700 mr-2">Observations:</span>
                  <span>{observationsCount}</span>
                </div>
                <div className="flex text-gray-500 items-center mb-1">
                  <span className="font-medium text-gray-700 mr-2">Conservation Status:</span>
                  <span>{conservationStatus}</span>
                </div>
                {wikipediaUrl && (
                  <a 
                    href={wikipediaUrl} 
                    target="_blank" 
                    rel="noopener noreferrer"
                    className="inline-block text-blue-500 hover:text-blue-400 underline mt-1"
                  >
                    Wikipedia
                  </a>
                )}
              </div>
              
              <div className="text-gray-500/75 text-sm overflow-y-auto pr-4">
                <p>{wikipediaText.substring(0, 300)}{wikipediaText.length > 300 ? '...' : ''}</p>
              </div>
            </div>
          </div>
        </div>
        
        {/* Right side: Image */}
        <div className="w-1/2 relative rounded-xl hidden md:block overflow-hidden">
          <div className="m-8 h-80">
            <img 
              src={imageUrl} 
              alt={commonName}
              className="w-full h-full p-4 rounded-xl drop-shadow-xl shadow-2xl object-cover transition-transform duration-1000 hover:scale-100"
              onError={(e) => {
                e.target.onerror = null;
                e.target.src = "https://via.placeholder.com/800?text=No+Image";
              }}
            />
          </div>
        </div>
      </div>
      
      {/* Navigation buttons and counter - moved outside the card */}
      {speciesList.length > 1 && (
        <div className="mt-6 flex justify-between items-center px-96">
          <button 
            onClick={goToPrev}
            disabled={isAnimating}
            className={`bg-slate-800 text-white rounded-full p-3 hover:bg-slate-700 transition-all transform hover:-translate-x-1 focus:outline-none focus:ring-2 focus:ring-gray-300 shadow-lg ${isAnimating ? 'opacity-50 cursor-not-allowed' : ''}`}
            aria-label="Previous species"
          >
            <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
            </svg>
          </button>
          
          <p className="text-gray-800 text-xl font-medium">
            {displayedIndex + 1} of {speciesList.length}
          </p>
          
          <button 
            onClick={goToNext}
            disabled={isAnimating}
            className={`bg-slate-800 text-white rounded-full p-3 hover:bg-slate-700 transition-all transform hover:translate-x-1 focus:outline-none focus:ring-2 focus:ring-gray-300 shadow-lg ${isAnimating ? 'opacity-50 cursor-not-allowed' : ''}`}
            aria-label="Next species"
          >
            <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
            </svg>
          </button>
        </div>
      )}

      {/* Add the simplified CSS for animations */}
      <style jsx>{`
        .card-container {
          transition: transform 1000ms ease, opacity 1000ms ease;
        }
        
        .slide-out-left {
          transform: translateX(-100%);
          opacity: 0;
        }
        
        .slide-out-right {
          transform: translateX(100%);
          opacity: 0;
        }
        
        /* Add these to your global CSS or tailwind.config.js for global use */
        @keyframes slideInFromRight {
          from {
            transform: translateX(100%);
            opacity: 0;
          }
          to {
            transform: translateX(0);
            opacity: 1;
          }
        }
        
        @keyframes slideInFromLeft {
          from {
            transform: translateX(-100%);
            opacity: 0;
          }
          to {
            transform: translateX(0);
            opacity: 1;
          }
        }
      `}</style>
    </div>
  );
};

// The rest of ExplorePage component stays the same
export default function ExplorePage() {
  const [searchTerm, setSearchTerm] = useState("");
  const [speciesList, setSpeciesList] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleSearch = async (event) => {
    event.preventDefault();
    setSpeciesList([]); // Clear previous results
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

      const reader = response.body.getReader();
      const decoder = new TextDecoder("utf-8");
      let buffer = "";

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split("\n\n");
        buffer = lines.pop() || "";

        for (const line of lines) {
          if (line.startsWith("data:")) {
            const jsonString = line.replace("data:", "").trim();
            try {
              const speciesData = JSON.parse(jsonString);
              setSpeciesList(prev => [...prev, speciesData]);
            } catch (error) {
              console.error("Error parsing species JSON:", error, jsonString);
            }
          }
        }
      }

      // Process any remaining data
      if (buffer.startsWith("data:")) {
        try {
          const jsonString = buffer.replace("data:", "").trim();
          const speciesData = JSON.parse(jsonString);
          setSpeciesList(prev => [...prev, speciesData]);
        } catch (error) {
          console.error("Error parsing final species JSON:", error);
        }
      }
    } catch (error) {
      console.error("Search error:", error);
      setError(error.message);
    } finally {
      setIsLoading(false);
    }
  };

  // For demonstration/testing purposes
  const loadSampleData = () => {
    const sampleData = [
      {
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
          },
          "audio": []
        }
      },
      {
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
          },
          "audio": ["https://www.xeno-canto.org/sounds/uploaded/SDPCHKOHRH/XC513247-Peacock1.mp3"]
        }
      },
      {
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
          },
          "audio": ["https://www.sound-ideas.com/preview/945/26037.mp3"]
        }
      }
    ];
    setSpeciesList(sampleData);
  };

  return (
    <div className="w-full">
      <div className="max-w-6xl mx-auto px-4 py-8">
        <form onSubmit={handleSearch} className="mb-10 ml-80">
          <div className="absolute bottom-4 justify w-md mx-auto rounded-full">
            <input
              type="search"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="block w-full p-4 pl-6 text-gray-900 rounded-full bg-slate-200/50 ring-1 ring-gray-300 focus:outline-none"
              placeholder="Search a location to explore species..."
              required
            />
            <button
              type="submit"
              className="absolute right-2.5 shadow-2xl bottom-2 bg-gray-900 hover:bg-gray-800 text-white rounded-full px-4 py-2 font-medium transition-colors"
            >
              Browse
            </button>
          </div>
        </form>
      </div>

      {isLoading && (
        <div className="flex justify-center items-center py-10">
          <div className="animate-spin rounded-full h-20 w-20 border-b-4 border-black-700"></div>
        </div>
      )}

      {error && (
        <div className="text-center text-red-500 py-8">
          <p>{error}</p>
          <button 
            onClick={() => loadSampleData()}
            className="mt-4 bg-gray-800 hover:bg-gray-700 text-white rounded-lg px-4 py-2 font-medium transition-colors"
          >
            Load Sample Data
          </button>
        </div>
      )}

      {!isLoading && speciesList.length === 0 && searchTerm && !error && (
        <p className="text-center text-gray-400 py-10">No species found for this location. Try another search.</p>
      )}

      <div className="max-w-6xl mx-auto px-4 mb-10">
        {!isLoading && speciesList.length > 0 && (
          <SpeciesCarousel speciesList={speciesList} />
        )}
      </div>

      {/* Example card for demonstration */}
      {!isLoading && speciesList.length === 0 && !searchTerm && !error && (
        <div className="flex justify-center text-center px-4 mt-10">
          <div className="absolute top-80 rounded-lg text-center">
            <button 
              onClick={() => loadSampleData()}
              className="mt-4 bg-gray-900 hover:bg-gray-800 text-white rounded-lg px-4 py-2 font-medium transition-colors"
            >
              Try sample data
            </button>
          </div>
        </div>
      )}
    </div>
  );
}