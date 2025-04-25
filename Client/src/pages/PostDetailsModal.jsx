import React from 'react';

function PostDetailsModal({ post, darkMode, onClose }) {
  if (!post) return null;
  
  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div 
        className={`${darkMode ? 'bg-gray-800 text-white' : 'bg-white text-gray-900'} 
          rounded-lg shadow-xl w-full max-w-4xl max-h-[90vh] overflow-y-auto`}
      >
        {/* Header with close button */}
        <div className="flex justify-between items-center p-4 border-b border-gray-200 dark:border-gray-700">
          <div className="flex items-center">
            <div className={`w-12 h-12 rounded-full ${darkMode ? 'bg-gray-600 text-gray-200' : 'bg-gray-300 text-gray-600'} flex items-center justify-center font-bold`}>
              {post.author?.charAt(1)?.toUpperCase() || '?'}
            </div>
            <div className="ml-3">
              <span className={`font-medium ${darkMode ? 'text-white' : 'text-gray-800'}`}>{post.author}</span>
              <div className={`text-xs ${darkMode ? 'text-gray-400' : 'text-gray-500'}`}>{post.timestamp || post.readTime}</div>
            </div>
          </div>
          <button 
            onClick={onClose}
            className={`p-2 rounded-full ${darkMode ? 'hover:bg-gray-700' : 'hover:bg-gray-100'}`}
          >
            <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
        
        {/* Content */}
        <div className="p-6">
          <h2 className={`text-2xl md:text-3xl font-bold mb-4 ${darkMode ? 'text-white' : ''}`}>{post.title}</h2>
          
          {/* Image */}
          {post.imageUrl && (
            <div className="mb-6">
              <img 
                src={post.imageUrl} 
                alt={post.title} 
                className="w-full h-64 md:h-96 object-cover rounded-lg"
              />
            </div>
          )}
          
          {/* Post text */}
          {post.postText && (
            <div className={`${darkMode ? 'text-gray-300' : 'text-gray-700'} text-lg leading-relaxed mb-6`}>
              <p>{post.postText}</p>
            </div>
          )}
          
          {/* Social stats */}
          {(post.likes !== undefined || post.likeCount !== undefined || post.shares !== undefined || post.shareCount !== undefined) && (
            <div className={`flex items-center justify-between pt-4 mt-2 border-t ${darkMode ? 'border-gray-700' : 'border-gray-200'}`}>
              <div className="flex space-x-4">
                <div className={`flex items-center space-x-1 ${darkMode ? 'text-gray-400' : 'text-gray-500'}`}>
                  <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                    <path strokeLinecap="round" strokeLinejoin="round" d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
                  </svg>
                  <span>{post.likes || post.likeCount || 0}</span>
                </div>
                
                <div className={`flex items-center space-x-1 ${darkMode ? 'text-gray-400' : 'text-gray-500'}`}>
                  <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                    <path strokeLinecap="round" strokeLinejoin="round" d="M8.684 13.342C8.886 12.938 9 12.482 9 12c0-.482-.114-.938-.316-1.342m0 2.684a3 3 0 110-2.684m0 2.684l6.632 3.316m-6.632-6l6.632-3.316m0 0a3 3 0 105.367-2.684 3 3 0 00-5.367 2.684zm0 9.316a3 3 0 105.368 2.684 3 3 0 00-5.368-2.684z" />
                  </svg>
                  <span>{post.shares || post.shareCount || 0}</span>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default PostDetailsModal;