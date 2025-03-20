import { useState, useRef, useEffect } from "react";

// Species Card Carousel Component
const SpeciesCarousel = ({ speciesList }) => {
  const [currentIndex, setCurrentIndex] = useState(0);
  const [isPlaying, setIsPlaying] = useState(false);
  const [slideDirection, setSlideDirection] = useState(null);
  const audioRef = useRef(null);

  // Handle navigation
  const goToNext = () => {
    setSlideDirection("right");
    setCurrentIndex((prevIndex) => (prevIndex + 1) % speciesList.length);
  };

  const goToPrev = () => {
    setSlideDirection("left");
    setCurrentIndex((prevIndex) => (prevIndex - 1 + speciesList.length) % speciesList.length);
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
    
    // Reset slide direction after animation completes
    const timer = setTimeout(() => {
      setSlideDirection(null);
    }, 500);
    
    return () => clearTimeout(timer);
  }, [currentIndex]);

  // Early return if no species data
  if (!speciesList || speciesList.length === 0) {
    return <div className="text-center text-gray-400">No species data available</div>;
  }

  // Get current species data
  const currentSpecies = speciesList[currentIndex];
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

  // Add animation classes based on slide direction
  const slideAnimationClass = slideDirection === "right" 
    ? "animate-slide-left" 
    : slideDirection === "left" 
      ? "animate-slide-right" 
      : "";

  return (
    <div className="relative w-full">
      {/* Hidden audio element */}
      <audio ref={audioRef} onEnded={() => setIsPlaying(false)} />
      
      {/* Card content with side-by-side layout */}
      <div className={`flex h-full w-full bg-black shadow-xl rounded-lg overflow-hidden transition-all duration-300 ${slideAnimationClass}`} style={{ height: "32rem" }}>
        {/* Left side: Content */}
        <div className="flex-1 p-6 md:p-8 overflow-y-auto relative">
          <div className="h-full flex flex-col">
            <div className="mb-4">
              <h2 className="text-3xl font-bold text-white mb-1">{commonName}</h2>
              
              <div className="flex items-center mb-4">
                <p className="text-xl italic text-gray-300">{scientificName}</p>
                
                {audioUrl && (
                  <button 
                    onClick={() => toggleAudio(audioUrl)} 
                    className={`ml-4 p-2 rounded-full ${
                      isPlaying 
                        ? "bg-red-600 hover:bg-red-700" 
                        : "bg-blue-600 hover:bg-blue-700"
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
              
              <div className="text-gray-300 mb-4">
                <div className="flex items-center mb-1">
                  <span className="font-medium text-gray-200 mr-2">Observations:</span>
                  <span>{observationsCount}</span>
                </div>
                <div className="flex items-center mb-1">
                  <span className="font-medium text-gray-200 mr-2">Conservation Status:</span>
                  <span>{conservationStatus}</span>
                </div>
                {wikipediaUrl && (
                  <a 
                    href={wikipediaUrl} 
                    target="_blank" 
                    rel="noopener noreferrer"
                    className="inline-block text-blue-400 hover:text-blue-300 hover:underline mt-1"
                  >
                    Wikipedia
                  </a>
                )}
              </div>
              
              <div className="text-gray-400 text-sm overflow-y-auto pr-4">
                <p>{wikipediaText.substring(0, 300)}{wikipediaText.length > 300 ? '...' : ''}</p>
              </div>
            </div>
          </div>
        </div>
        
        {/* Right side: Image */}
        <div className="w-1/2 relative hidden md:block overflow-hidden">
          <img 
            src={imageUrl} 
            alt={commonName}
            className="w-full h-full object-cover transition-transform duration-500 hover:scale-110"
            onError={(e) => {
              e.target.onerror = null;
              e.target.src = "https://via.placeholder.com/800?text=No+Image";
            }}
          />
        </div>
      </div>
      
      {/* Navigation buttons and counter - moved outside the card */}
      {speciesList.length > 1 && (
        <div className="mt-6 flex justify-between items-center px-4">
          <button 
            onClick={goToPrev}
            className="bg-slate-800 text-white rounded-full p-3 hover:bg-slate-700 transition-all transform hover:-translate-x-1 focus:outline-none focus:ring-2 focus:ring-blue-300 shadow-lg"
            aria-label="Previous species"
          >
            <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
            </svg>
          </button>
          
          <p className="text-gray-300 text-lg font-medium">
            {currentIndex + 1} of {speciesList.length}
          </p>
          
          <button 
            onClick={goToNext}
            className="bg-slate-800 text-white rounded-full p-3 hover:bg-slate-700 transition-all transform hover:translate-x-1 focus:outline-none focus:ring-2 focus:ring-blue-300 shadow-lg"
            aria-label="Next species"
          >
            <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
            </svg>
          </button>
        </div>
      )}
    </div>
  );
};

// Updated ExplorePage component to use the carousel
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
        <form onSubmit={handleSearch} className="mb-10">
          <div className="relative max-w-md mx-auto">
            <input
              type="search"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="block w-full p-4 pl-6 text-gray-300 rounded-lg bg-slate-900 focus:ring-1 focus:ring-blue-300 focus:outline-none"
              placeholder="Enter a location to explore species..."
              required
            />
            <button
              type="submit"
              className="absolute right-2.5 bottom-2.5 bg-blue-600 hover:bg-blue-700 text-white rounded-lg px-4 py-2 font-medium transition-colors"
            >
              Search
            </button>
          </div>
        </form>
      </div>

      {isLoading && (
        <div className="flex justify-center items-center py-10">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-700"></div>
        </div>
      )}

      {error && (
        <div className="text-center text-red-500 py-8">
          <p>{error}</p>
          <button 
            onClick={() => loadSampleData()}
            className="mt-4 bg-blue-600 hover:bg-blue-700 text-white rounded-lg px-4 py-2 font-medium transition-colors"
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
        <div className="max-w-6xl mx-auto px-4 mt-10">
          <p className="text-center text-gray-400 mb-6">Search for a location to explore species</p>
          <div className="bg-slate-900 p-6 rounded-lg text-center">
            <p className="text-xl text-gray-300">Enter a location like "Amazon Rainforest", "Arctic", or "Madagascar" to discover species</p>
            <button 
              onClick={() => loadSampleData()}
              className="mt-4 bg-blue-600 hover:bg-blue-700 text-white rounded-lg px-4 py-2 font-medium transition-colors"
            >
              Or try sample data
            </button>
          </div>
        </div>
      )}
    </div>
  );
}

