import React, { useState } from 'react';

function PostCard({ author, title, postText, likeCount, shareCount, imageUrl, timestamp, darkMode }) {
  const [likes, setLikes] = useState(likeCount);
  const [shares, setShares] = useState(shareCount);
  const [isLiked, setIsLiked] = useState(false);
  const [isShared, setIsShared] = useState(false);
  
  const handleLike = () => {
    if (isLiked) {
      setLikes(prev => prev - 1);
      setIsLiked(false);
    } else {
      setLikes(prev => prev + 1);
      setIsLiked(true);
    }
  };
  
  const handleShare = () => {
    if (!isShared) {
      setShares(prev => prev + 1);
      setIsShared(true);
      // In a real app, you might open a share dialog here
    }
  };

  return (
    <div className={`${darkMode ? 'bg-gray-800 text-white' : 'bg-white text-gray-900'} rounded-lg overflow-hidden shadow-md hover:shadow-lg transition-shadow`}>
      <div className="p-4 md:p-6">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center">
            <div className={`w-10 h-10 rounded-full ${darkMode ? 'bg-gray-600 text-gray-200' : 'bg-gray-300 text-gray-600'} flex items-center justify-center font-bold`}>
              {author.charAt(1).toUpperCase()}
            </div>
            <div className="ml-3">
              <span className={`font-medium ${darkMode ? 'text-white' : 'text-gray-800'}`}>{author}</span>
              <div className={`text-xs ${darkMode ? 'text-gray-400' : 'text-gray-500'}`}>{timestamp}</div>
            </div>
          </div>
          <button className={`${darkMode ? 'text-gray-400 hover:text-gray-200' : 'text-gray-500 hover:text-gray-700'}`}>
            <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
              <path d="M6 10a2 2 0 11-4 0 2 2 0 014 0zM12 10a2 2 0 11-4 0 2 2 0 014 0zM16 12a2 2 0 100-4 2 2 0 000 4z" />
            </svg>
          </button>
        </div>
        
        <div className="flex flex-col md:flex-row gap-4">
          <div className="flex-1">
            <h3 className={`text-xl md:text-2xl font-bold mb-3 ${darkMode ? 'text-white' : ''}`}>{title}</h3>
            <p className={`${darkMode ? 'text-gray-300' : 'text-gray-700'} mb-4`}>{postText}</p>
          </div>
          
          {imageUrl && (
            <div className="md:w-1/3 lg:w-1/4">
              <div className="rounded-lg overflow-hidden h-full">
                <img 
                  src={imageUrl} 
                  alt={title} 
                  className="w-full h-48 md:h-full object-cover"
                />
              </div>
            </div>
          )}
        </div>
        
        <div className={`flex items-center justify-between pt-4 mt-2 border-t ${darkMode ? 'border-gray-700' : 'border-gray-100'}`}>
          <div className="flex space-x-4">
            <button 
              onClick={handleLike}
              className={`flex items-center space-x-1 ${isLiked ? 'text-blue-600' : darkMode ? 'text-gray-400' : 'text-gray-500'} hover:text-blue-600`}
            >
              <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" fill={isLiked ? "currentColor" : "none"} viewBox="0 0 24 24" stroke="currentColor" strokeWidth={isLiked ? "0" : "2"}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
              </svg>
              <span>{likes}</span>
            </button>
            
            <button 
              onClick={handleShare}
              className={`flex items-center space-x-1 ${isShared ? 'text-green-600' : darkMode ? 'text-gray-400' : 'text-gray-500'} hover:text-green-600`}
            >
              <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M8.684 13.342C8.886 12.938 9 12.482 9 12c0-.482-.114-.938-.316-1.342m0 2.684a3 3 0 110-2.684m0 2.684l6.632 3.316m-6.632-6l6.632-3.316m0 0a3 3 0 105.367-2.684 3 3 0 00-5.367 2.684zm0 9.316a3 3 0 105.368 2.684 3 3 0 00-5.368-2.684z" />
              </svg>
              <span>{shares}</span>
            </button>
          </div>
          
          <button className={`${darkMode ? 'text-gray-400 hover:text-gray-200' : 'text-gray-500 hover:text-gray-700'}`}>
            <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M5 5a2 2 0 012-2h10a2 2 0 012 2v16l-7-3.5L5 21V5z" />
            </svg>
          </button>
        </div>
      </div>
    </div>
  );
}

export default PostCard;