import React, { useState, useEffect } from "react";
import "@pages/GalleryPage.css";
import searchIcon from "@assets/searchicon.svg"
function GalleryPage() {
  const [query, setQuery] = useState("red panda");
  const [loading, setLoading] = useState(false);
  const [data, setData] = useState([]);

  const apiKey = import.meta.env.VITE_PEXELS_KEY;
  const getPictures = async () => {
    setLoading(true);
    await fetch(`https://api.pexels.com/v1/search?query=${query}`, {
      headers: {
        Authorization: apiKey,
      },
    })
      .then((resp) => {
        return resp.json();
      })
      .then((res) => {
        setLoading(false);
        setData(res.photos);
      });
  };

  useEffect(() => {
    getPictures();
  }, []);

  const onKeyDownHandler = (e) => {
    if (e.keyCode === 13) {
      getPictures();
    }
  };

  const handleQueryChange = (e) => {
    setQuery(e.target.value);
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <div className="header py-10">
        <div className="flex justify-center mt-1">
          <div className="flex p-2 max-w-xl border-1 border-gray-500/50 bg-gray-100 rounded-full">
            <img src={searchIcon} height={24} width={24} className="" alt="" />
            <input
              className="w-80 h-10 py-1 px-3 focus:outline-none text-gray-700"
              onKeyDown={onKeyDownHandler}
              placeholder="Search for Anything..."
              onChange={handleQueryChange}
              value={query}
            />
            <button 
              onClick={getPictures}
              className=" ml-2 h-10 bg-gray-900 text-white py-1 px-4 rounded-full hover:bg-gray-900/75 transition-colors"
            >
              Search
            </button>
          </div>
        </div>
      </div>

      

      <div className="bento-grid grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4 my-2">
        {data?.map((item, index) => {
          // Assign random height class to create masonry-like effect
          const heightClass = index % 5 === 0 ? "row-span-2" : "";
          // Every 7th image spans 2 columns for wider images
          const widthClass = index % 7 === 0 ? "col-span-2" : "";
          
          return (
            <div 
              key={item.id} 
              className={`bento-item relative overflow-hidden rounded-xl ${heightClass} ${widthClass} transition-all duration-300 hover:shadow-xl group`}
            >
              <img 
                src={item.src.large} 
                alt={item.photographer} 
                className="w-full h-full object-cover"
              />
              <div className="absolute inset-0 bg-gradient-to-t from-black/50 via-black/20 to-transparent opacity-1 group-hover:opacity-100 transition duration-300">
                <div className="absolute bottom-0 left-0 right-0 p-4 text-white">
                  <p className="font-medium">{item.photographer}</p>
                  <div className="flex justify-between items-center mt-2">
                    <span className="text-sm">{item.width} × {item.height}</span>
                    <a
                      href={item.src.original}
                      download
                      className="w-8 bg-gray-800 fl backdrop-blur-sm p-2 rounded-xl "
                      target="_blank"
                      rel="noopener noreferrer"
                    >
                      &rarr;
                    </a>
                  </div>
                </div>
              </div>
            </div>
          );
        })}
      </div>
      
      {data?.length === 0 && !loading && (
        <div className="text-center py-12 text-gray-500">
          No images found. Try a different search term.
        </div>
      )}
    </div>
  );
}

export default GalleryPage;